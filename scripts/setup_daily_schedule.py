#!/usr/bin/env python3
"""CIVID daily schedule setup helper.

Prints commands to schedule the daily pipeline run on Windows Task Scheduler
or Unix cron. Does not modify system settings automatically; prints the
command for the user to copy-paste.

Usage:
  python scripts/setup_daily_schedule.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
SCRIPT = REPO / "scripts" / "run_pipeline.py"


def windows_task():
    name = "CIVID Daily Update"
    tr = f'"{PYTHON}" "{SCRIPT}"'
    cmd = (
        f'schtasks /Create /TN "{name}" '
        f'/TR "{tr}" '
        f'/SC DAILY /ST 02:00 /F'
    )
    print("Windows Task Scheduler (daily at 02:00):")
    print(f"  {cmd}")
    print()


def cron_job():
    cmd = f"0 2 * * * {PYTHON} {SCRIPT}"
    print("Cron (daily at 02:00):")
    print(f"  {cmd}")
    print()


def main():
    print("=== CIVID Daily Schedule Setup ===")
    print(f"Repository: {REPO}")
    print(f"Python:     {PYTHON}")
    print(f"Script:     {SCRIPT}")
    print()
    if os.name == "nt":
        windows_task()
    else:
        cron_job()
    print("After scheduling, the pipeline will run automatically every day.")
    print("Run logs are written to output/run_log.json.")


if __name__ == "__main__":
    main()
