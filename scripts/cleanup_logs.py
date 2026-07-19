#!/usr/bin/env python3
"""CIVID log cleanup utility.

Trims output/run_log.json to keep only the most recent N entries
(default: 200). Also archives old logs to output/archived_logs/ if needed.

Run:
  python scripts/cleanup_logs.py
  python scripts/cleanup_logs.py --keep 100
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
LOG_PATH = OUTPUT / "run_log.json"
ARCHIVE_DIR = OUTPUT / "archived_logs"


def load_logs():
    if not LOG_PATH.exists():
        return []
    try:
        return json.load(open(LOG_PATH, encoding="utf-8"))
    except Exception:
        return []


def save_logs(logs):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def archive_old_logs(logs, keep):
    if len(logs) <= keep:
        return
    archive = logs[:-keep]
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    path = ARCHIVE_DIR / f"run_log_archive_{stamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    print(f"[ok] Archived {len(archive)} old log entries to {path}")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", type=int, default=200, help="Number of recent log entries to keep")
    args = ap.parse_args()

    logs = load_logs()
    print(f"[info] Loaded {len(logs)} log entries from {LOG_PATH}")

    if len(logs) > args.keep:
        archive_old_logs(logs, args.keep)
        logs = logs[-args.keep:]
        save_logs(logs)
        print(f"[ok] Trimmed run_log.json to {len(logs)} entries")
    else:
        print("[ok] No cleanup needed")


if __name__ == "__main__":
    main()
