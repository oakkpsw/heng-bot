import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from availability import AvailabilityManager


def test_submit_and_get_availability(tmp_path):
    db = tmp_path / "test.db"
    manager = AvailabilityManager(db_path=str(db))
    manager.submit_availability("user1", ["2024-05-01T10:00", "2024-05-02T10:00"])

    avail = manager.get_availability("user1")
    assert avail is not None
    assert avail.timeslots == ["2024-05-01T10:00", "2024-05-02T10:00"]


def test_list_missing_users(tmp_path):
    db = tmp_path / "test.db"
    manager = AvailabilityManager(db_path=str(db))
    manager.submit_availability("user1", ["slot1"])

    missing = manager.list_missing_users(["user1", "user2", "user3"])
    assert missing == ["user2", "user3"]
