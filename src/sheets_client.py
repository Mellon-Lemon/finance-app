from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import get_google_sheet_id, get_secret, get_service_account_info


SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

TRANSACTION_COLUMNS = [
    "Datum",
    "Ticker",
    "Type",
    "Aantal",
    "Prijs per stuk",
    "Kosten",
    "Totaal",
    "Valuta",
]


class SheetsConfigError(RuntimeError):
    """Raised when Google Sheets configuration is missing or incomplete."""


@dataclass(frozen=True)
class SheetsConfig:
    sheet_id: str
    service_account_file: Path | None = None
    service_account_info: dict[str, Any] | None = None


class GoogleSheetsClient:
    def __init__(self, config: SheetsConfig) -> None:
        self._config = config
        self._spreadsheet = None

    @classmethod
    def from_environment(cls) -> "GoogleSheetsClient":
        sheet_id = (get_google_sheet_id() or "").strip()

        if not sheet_id:
            raise SheetsConfigError("GOOGLE_SHEET_ID ontbreekt.")

        service_account_info = get_service_account_info()

        if service_account_info:
            return cls(
                SheetsConfig(
                    sheet_id=sheet_id,
                    service_account_info=service_account_info,
                )
            )

        credentials_file = (
            (get_secret("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip()
            or (get_secret("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
        )

        if not credentials_file:
            raise SheetsConfigError(
                "Google credentials ontbreken. Gebruik lokaal "
                "GOOGLE_SERVICE_ACCOUNT_FILE of online GOOGLE_SERVICE_ACCOUNT_JSON."
            )

        credentials_path = Path(credentials_file).expanduser()

        if not credentials_path.exists():
            raise SheetsConfigError(
                f"Service account file bestaat niet: {credentials_path}"
            )

        return cls(
            SheetsConfig(
                sheet_id=sheet_id,
                service_account_file=credentials_path,
            )
        )

    def get_records(self, worksheet_name: str) -> list[dict[str, object]]:
        worksheet = self._get_spreadsheet().worksheet(worksheet_name)
        return worksheet.get_all_records(numericise_ignore=["all"])

    def try_get_records(self, worksheet_name: str) -> list[dict[str, object]]:
        try:
            return self.get_records(worksheet_name)
        except Exception:
            return []

    def get_transaction_rows(self) -> list[dict[str, object]]:
        worksheet = self._get_spreadsheet().worksheet("Transacties")
        values = worksheet.get_all_values()
        if not values:
            return []

        headers = values[0]
        rows: list[dict[str, object]] = []
        for sheet_row, row_values in enumerate(values[1:], start=2):
            record = {
                column: _get_by_header(headers, row_values, column)
                for column in TRANSACTION_COLUMNS
            }
            if not any(str(value).strip() for value in record.values()):
                continue
            record["Sheet rij"] = sheet_row
            rows.append(record)
        return rows

    def try_get_transaction_rows(self) -> list[dict[str, object]]:
        try:
            return self.get_transaction_rows()
        except Exception:
            return []

    def append_transaction(self, row: dict[str, object]) -> None:
        values = [row.get(column, "") for column in TRANSACTION_COLUMNS]
        worksheet = self._get_spreadsheet().worksheet("Transacties")
        worksheet.append_row(values, value_input_option="USER_ENTERED")

    def delete_transaction_row(
        self,
        sheet_row: int,
        expected_row: dict[str, object],
    ) -> None:
        if sheet_row < 2:
            raise ValueError("Ongeldig rijnummer voor Transacties.")

        worksheet = self._get_spreadsheet().worksheet("Transacties")
        values = worksheet.get_all_values()
        if len(values) < sheet_row:
            raise ValueError("Transactie bestaat niet meer in Google Sheets.")

        headers = values[0]
        current_values = values[sheet_row - 1]
        current_row = {
            column: _get_by_header(headers, current_values, column)
            for column in TRANSACTION_COLUMNS
        }

        for column in TRANSACTION_COLUMNS:
            expected_value = expected_row.get(column, "")
            if _normalise_cell(current_row.get(column, "")) != _normalise_cell(expected_value):
                raise ValueError("Transactie is gewijzigd sinds de preview. Laad data opnieuw.")

        worksheet.delete_rows(sheet_row)

    def update_saldo(self, account: str, new_value: float) -> None:
        worksheet = self._get_spreadsheet().worksheet("Saldi")
        values = worksheet.get_all_values()
        if not values:
            raise ValueError("Tabblad Saldi bevat geen headers.")

        headers = values[0]
        account_col = _find_column(headers, "Account")
        balance_col = _find_column(headers, "Huidig Saldo")
        if account_col is None or balance_col is None:
            raise ValueError("Tabblad Saldi mist kolommen Account of Huidig Saldo.")

        target_row = None
        for row_index, row in enumerate(values[1:], start=2):
            if len(row) >= account_col and row[account_col - 1].strip() == account:
                target_row = row_index
                break

        if target_row is None:
            raise ValueError(f"Account niet gevonden in Saldi: {account}")

        worksheet.update_cell(target_row, balance_col, new_value)

    def _get_spreadsheet(self):
        if self._spreadsheet is None:
            self._spreadsheet = self._open_spreadsheet()
        return self._spreadsheet

    def _open_spreadsheet(self):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except ImportError as exc:
            raise SheetsConfigError(
                "Google Sheets dependencies ontbreken. Installeer requirements.txt."
            ) from exc

        if self._config.service_account_info:
            credentials = Credentials.from_service_account_info(
                self._config.service_account_info,
                scopes=[SHEETS_SCOPE],
            )
        elif self._config.service_account_file:
            credentials = Credentials.from_service_account_file(
                self._config.service_account_file,
                scopes=[SHEETS_SCOPE],
            )
        else:
            raise SheetsConfigError("Google service account credentials ontbreken.")

        return gspread.authorize(credentials).open_by_key(self._config.sheet_id)


GoogleSheetsReadOnlyClient = GoogleSheetsClient


def _find_column(headers: list[str], expected: str) -> int | None:
    expected_key = _normalise_header(expected)
    for index, header in enumerate(headers, start=1):
        if _normalise_header(header) == expected_key:
            return index
    return None


def _get_by_header(headers: list[str], row: list[str], expected: str) -> object:
    column = _find_column(headers, expected)
    if column is None or len(row) < column:
        return ""
    return row[column - 1]


def _normalise_header(value: str) -> str:
    return str(value).strip().lower().replace(".", "")


def _normalise_cell(value: object) -> str:
    return str(value).strip()