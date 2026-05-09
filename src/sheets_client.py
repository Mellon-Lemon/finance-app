from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
    service_account_file: Path


class GoogleSheetsClient:
    def __init__(self, config: SheetsConfig) -> None:
        self._config = config
        self._spreadsheet = None

    @classmethod
    def from_environment(cls) -> "GoogleSheetsClient":
        sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()
        credentials_file = (
            os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        )

        if not sheet_id:
            raise SheetsConfigError("GOOGLE_SHEET_ID ontbreekt.")
        if not credentials_file:
            raise SheetsConfigError(
                "GOOGLE_SERVICE_ACCOUNT_FILE of GOOGLE_APPLICATION_CREDENTIALS ontbreekt."
            )

        credentials_path = Path(credentials_file).expanduser()
        if not credentials_path.exists():
            raise SheetsConfigError(
                f"Service account file bestaat niet: {credentials_path}"
            )

        return cls(SheetsConfig(sheet_id=sheet_id, service_account_file=credentials_path))

    def get_records(self, worksheet_name: str) -> list[dict[str, object]]:
        worksheet = self._get_spreadsheet().worksheet(worksheet_name)
        return worksheet.get_all_records(numericise_ignore=["all"])

    def try_get_records(self, worksheet_name: str) -> list[dict[str, object]]:
        try:
            return self.get_records(worksheet_name)
        except Exception:
            return []

    def append_transaction(self, row: dict[str, object]) -> None:
        values = [row.get(column, "") for column in TRANSACTION_COLUMNS]
        worksheet = self._get_spreadsheet().worksheet("Transacties")
        worksheet.append_row(values, value_input_option="USER_ENTERED")

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

        credentials = Credentials.from_service_account_file(
            self._config.service_account_file,
            scopes=[SHEETS_SCOPE],
        )
        return gspread.authorize(credentials).open_by_key(self._config.sheet_id)


GoogleSheetsReadOnlyClient = GoogleSheetsClient


def _find_column(headers: list[str], expected: str) -> int | None:
    expected_key = _normalise_header(expected)
    for index, header in enumerate(headers, start=1):
        if _normalise_header(header) == expected_key:
            return index
    return None


def _normalise_header(value: str) -> str:
    return str(value).strip().lower().replace(".", "")
