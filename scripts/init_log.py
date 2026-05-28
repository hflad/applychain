#!/usr/bin/env python3
"""
init_log.py — Initialize the applications_log.csv file.
Run once during setup: python3 scripts/init_log.py
"""

import csv
import os
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "applications_log.csv"

COLUMNS = [
    "date",
    "company",
    "role",
    "jd_url",
    "ats_platform",
    "status",
    "resume_file",
    "cover_letter_file",
    "match_score",
    "notes",
]


def init_log():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if LOG_PATH.exists():
        print(f"Log already exists at {LOG_PATH} — skipping.")
        return

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

    print(f"Created {LOG_PATH}")
    print(f"Columns: {', '.join(COLUMNS)}")


if __name__ == "__main__":
    init_log()
