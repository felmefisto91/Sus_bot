import logging
import threading
import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

import config


logger = logging.getLogger("AllianceSiegeBot.Sheets")

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_current_week_start_date() -> str:
    """Return the Wednesday 13:00 Kyiv-time siege-week key as YYYY-MM-DD."""
    now = datetime.datetime.now(config.KYIV_TZ)
    # weekday(): Monday=0, ..., Wednesday=2, ..., Sunday=6
    days_since_wednesday = (now.weekday() - 2) % 7
    wednesday_date = now.date() - datetime.timedelta(days=days_since_wednesday)
    if now.weekday() == 2 and now.hour < 13:
        wednesday_date -= datetime.timedelta(days=7)
    return wednesday_date.strftime("%Y-%m-%d")


class SheetsManager:
    """Lazily creates and reuses the Google Sheets client for this process."""

    _instance: Optional["SheetsManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._client: Optional[gspread.Client] = None
        self._spreadsheets: dict[str, gspread.Spreadsheet] = {}

    @classmethod
    def get_instance(cls) -> "SheetsManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get_client(self) -> gspread.Client:
        if self._client is None:
            credentials = Credentials.from_service_account_file(
                config.GOOGLE_CREDS_FILE,
                scopes=_SCOPES,
            )
            self._client = gspread.authorize(credentials)
            logger.info("✅ Успішно авторизовано Google Sheets клієнт.")
        return self._client

    def get_spreadsheet(self) -> gspread.Spreadsheet:
        if config.SPREADSHEET_ID not in self._spreadsheets:
            self._spreadsheets[config.SPREADSHEET_ID] = self.get_client().open_by_key(
                config.SPREADSHEET_ID
            )
        return self._spreadsheets[config.SPREADSHEET_ID]

    def get_worksheet(
        self,
        worksheet_name: str,
        default_headers: Optional[list[str]] = None,
    ) -> gspread.Worksheet:
        """Get a worksheet, creating it and its headers when needed."""
        spreadsheet = self.get_spreadsheet()
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            logger.info("📄 Створюємо вкладку '%s' в таблиці...", worksheet_name)
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            if default_headers:
                worksheet.append_row(default_headers)
            return worksheet

        if default_headers and not worksheet.get_all_values():
            worksheet.append_row(default_headers)
        return worksheet

    def remove_roster_row(self, corp: str, system: str):
        """Remove a system from the alliance roster sheet."""
        sheet = self.get_worksheet(config.ALLIANCE_ROSTER_SHEET)
        values = sheet.get_all_values()

        for i, row in enumerate(values):
            if len(row) >= 2 and row[0].strip() == corp and row[1].strip() == system:
                # gspread delete_rows(index, count)
                # index is 1-based.
                sheet.delete_rows(i + 1)
                return True
        logger.warning("⚠️ System %s for corp %s not found in roster sheet.", system, corp)
        return False

    def update_roster_row(self, corp: str, system: str, region: str, old_system: Optional[str] = None):
        """Add or update a system in the alliance roster sheet."""
        sheet = self.get_worksheet(config.ALLIANCE_ROSTER_SHEET)
        values = sheet.get_all_values()

        if old_system:
            # Search for the row with (corp, old_system)
            for i, row in enumerate(values):
                if len(row) >= 2 and row[0].strip() == corp and row[1].strip() == old_system:
                    # Found the row. Update it.
                    # gspread indices are 1-based, and row 1 is header.
                    sheet.update(range_name=f"A{i+1}:C{i+1}", values=[[corp, system, region]])
                    return True
            logger.warning("⚠️ System %s for corp %s not found in roster sheet.", old_system, corp)
            return False
        else:
            # Append new row
            sheet.append_row([corp, system, region])
            return True

    def get_progress_worksheet(self, default_headers: Optional[list[str]] = None) -> gspread.Worksheet:
        """Get the worksheet for the current siege week (Alliance_Siege_YYYY-MM-DD)."""
        week_date = get_current_week_start_date()
        sheet_name = f"{config.ALLIANCE_SIEGE_SHEET_PREFIX}_{week_date}"
        return self.get_worksheet(sheet_name, default_headers=default_headers)


sheets_service = SheetsManager.get_instance()
