"""Configuration for the standalone Alliance Siege bot.

The service intentionally has its own .env file so it can run with a separate
Discord application and without inheriting configuration from the main bot.
"""

import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def _int_env(name: str, default: int = 0) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} має бути числовим Discord ID") from error


def _id_list_env(name: str) -> list[int]:
    raw_value = os.getenv(name, "").strip()
    if not raw_value:
        return []
    try:
        return [int(value.strip()) for value in raw_value.split(",") if value.strip()]
    except ValueError as error:
        raise ValueError(f"{name} має містити Discord ID через кому") from error


# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
ALLIANCE_SIEGE_CHANNEL_ID = _int_env("ALLIANCE_SIEGE_CHANNEL_ID")
OFFICER_ROLES = _id_list_env("OFFICER_ROLE_IDS")
SIEGE_ROLE_ID = _int_env("SIEGE_ROLE_ID")

# Google Sheets
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json").strip()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "").strip()
ALLIANCE_ROSTER_SHEET = os.getenv("ALLIANCE_ROSTER_SHEET", "Alliance_Roster").strip()
ALLIANCE_SIEGE_SHEET_PREFIX = os.getenv("ALLIANCE_SIEGE_SHEET", "Alliance_Siege").strip()

# Database
DB_PATH = os.getenv("DB_PATH", "alliance_siege.db").strip()
DB_SYNC_INTERVAL = 300  # Sync to Google Sheets every 5 minutes

# Time
KYIV_TZ = ZoneInfo("Europe/Kyiv")


def validate_configuration() -> None:
    """Fail before connecting to Discord when required settings are absent."""
    missing = []
    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")
    if not SPREADSHEET_ID:
        missing.append("SPREADSHEET_ID")
    if not ALLIANCE_SIEGE_CHANNEL_ID:
        missing.append("ALLIANCE_SIEGE_CHANNEL_ID")

    if missing:
        raise ValueError("Не задано обов'язкові змінні: " + ", ".join(missing))
    if not os.path.isfile(GOOGLE_CREDS_FILE):
        raise ValueError(f"Не знайдено файл облікових даних Google: {GOOGLE_CREDS_FILE}")
