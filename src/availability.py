from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlite3

@dataclass
class Availability:
    user_id: str
    timeslots: List[str]  # Represented as ISO formatted strings


class AvailabilityManager:
    """Store and retrieve availability from a SQLite DB."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS availability (
                user_id TEXT PRIMARY KEY,
                timeslots TEXT
            )
            """
        )
        self.conn.commit()

    def submit_availability(self, user_id: str, timeslots: List[str]) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO availability (user_id, timeslots) VALUES (?, ?)",
            (user_id, ",".join(timeslots)),
        )
        self.conn.commit()

    def get_availability(self, user_id: str) -> Optional[Availability]:
        cur = self.conn.cursor()
        cur.execute("SELECT timeslots FROM availability WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return Availability(user_id=user_id, timeslots=row[0].split(","))
        return None

    def list_missing_users(self, group_members: List[str]) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM availability")
        responded = {row[0] for row in cur.fetchall()}
        return [uid for uid in group_members if uid not in responded]

