import sqlite3
import logging
from typing import List, Tuple, Dict, Optional
import config

logger = logging.getLogger("AllianceSiegeBot.DB")

class DatabaseManager:
    """Handles local SQLite caching for Alliance Siege data."""

    def __init__(self):
        self.db_path = config.DB_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            # Roster table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roster (
                    corp TEXT,
                    system TEXT,
                    region TEXT,
                    PRIMARY KEY (corp, system)
                )
            """)
            # Progress table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    corp TEXT,
                    system TEXT,
                    status TEXT,
                    cleared_by TEXT,
                    cleared_at TEXT,
                    week_date TEXT,
                    PRIMARY KEY (corp, system, week_date),
                    FOREIGN KEY (corp, system) REFERENCES roster(corp, system)
                )
            """)
            conn.commit()

    def sync_roster(self, roster_data: List[Tuple[str, str, str]]):
        """Sync roster from Google Sheets to DB."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM roster")
            conn.executemany(
                "INSERT INTO roster (corp, system, region) VALUES (?, ?, ?)",
                roster_data
            )
            conn.commit()
            logger.info("✅ Roster synced to DB.")

    def sync_progress(self, progress_data: List[Tuple[str, str, str, str, str, str]]):
        """Sync progress from Google Sheets to DB."""
        # progress_data: (week_date, corp, system, status, cleared_by, cleared_at)
        with self._get_connection() as conn:
            # We only sync the current week's data usually, but for simplicity
            # we can replace all progress and reload current week.
            conn.execute("DELETE FROM progress")
            conn.executemany(
                "INSERT INTO progress (week_date, corp, system, status, cleared_by, cleared_at) VALUES (?, ?, ?, ?, ?, ?)",
                progress_data
            )
            conn.commit()
            logger.info("✅ Progress synced to DB.")

    def update_progress(self, week_date: str, corp: str, system: str, status: str, cleared_by: str, cleared_at: str):
        """Update a specific system status in DB."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO progress (week_date, corp, system, status, cleared_by, cleared_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(corp, system, week_date) DO UPDATE SET
                    status=excluded.status,
                    cleared_by=excluded.cleared_by,
                    cleared_at=excluded.cleared_at
            """, (week_date, corp, system, status, cleared_by, cleared_at))
            conn.commit()

    def add_system(self, corp: str, system: str, region: str):
        """Add a new system to the roster."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO roster (corp, system, region) VALUES (?, ?, ?)",
                (corp, system, region)
            )
            conn.commit()

    def update_system(self, corp: str, old_system: str, new_system: str, new_region: str):
        """Update an existing system in the roster."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE roster SET system = ?, region = ? WHERE corp = ? AND system = ?",
                (new_system, new_region, corp, old_system)
            )
            conn.commit()

    def remove_system(self, corp: str, system: str):
        """Remove a system from the roster."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM roster WHERE corp = ? AND system = ?", (corp, system))
            conn.commit()

    def get_roster(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get all roster data as a dictionary."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT corp, system, region FROM roster")
            roster = {}
            for corp, system, region in cursor.fetchall():
                roster.setdefault(corp, []).append((system, region))
            return roster

    def get_progress(self, week_date: str) -> Dict[Tuple[str, str], Dict[str, str]]:
        """Get progress for a specific week."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT corp, system, status, cleared_by FROM progress WHERE week_date = ?",
                (week_date,)
            )
            progress = {}
            for corp, system, status, cleared_by in cursor.fetchall():
                progress[(corp, system)] = {
                    "status": status,
                    "cleared_by": cleared_by,
                }
            return progress

    def get_pending_updates(self, week_date: str) -> List[Tuple[str, str, str, str, str, str]]:
        """Get all data for the current week to sync back to Sheets."""
        # In a real app, we'd track "dirty" flags.
        # For simplicity, we'll return all progress for the week.
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT week_date, corp, system, status, cleared_by, cleared_at FROM progress WHERE week_date = ?",
                (week_date,)
            )
            return cursor.fetchall()

db_manager = DatabaseManager()
