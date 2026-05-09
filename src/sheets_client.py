from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


READ_ONLY_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


class SheetsConfigError(RuntimeError):
    """Raised when Google Sheets configuration is missing or incomplete."""


@dataclass(frozen=True)
class SheetsConfig:
    sheet_id: str
    service_account_file: Path


class GoogleSheetsReadOnlyClient:
    def __init__(self, config: SheetsConfig) -> None:
        self._config = config
        self._spreadsheet = None

    @classmethod
    def from_environment(cls) -> "GoogleSheetsReadOnlyClient":
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
        return worksheet.get_all_records()

    def try_get_records(self, worksheet_name: str) -> list[dict[str, object]]:
        try:
            return self.get_records(worksheet_name)
        except Exception:
            return []

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
            scopes=[READ_ONLY_SCOPE],
        )
        return gspread.authorize(credentials).open_by_key(self._config.sheet_id)
