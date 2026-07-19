#!/usr/bin/env python3
"""CIVID full pipeline orchestrator with scheduling, error handling, and status tracking.

Steps:
  1. validate_dataset.py
  2. renumber_records.py
  3. generate_news_intelligence.py
  4. build_exports.py
  5. generate_html_dashboard.py
  6. infographic.py (optional)
  7. phase_orchestrator.py (optional)

Run modes:
  python scripts/run_pipeline.py            # run full pipeline
  python scripts/run_pipeline.py --no-infographic  # skip image generation
  python scripts/run_pipeline.py --no-phase-check   # skip phase orchestrator
  python scripts/run_pipeline.py --schedule          # print Windows Task Scheduler / cron command

Exit codes:
  0 = success
  1 = validation error or pipeline failure
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
EXPORTS = REPO / "exports"
SCRIPTS = REPO / "scripts"


def run_step(name, cmd, log_path):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        dur = round(time.time() - t0, 2)
        status = "success" if p.returncode == 0 else "failed"
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "step": name,
            "status": status,
            "duration": dur,
            "records_added": 0,
            "records_reviewed": 0,
            "errors": [{"step": name, "message": p.stderr.strip()}] if p.returncode != 0 else [],
        }
        if p.stdout.strip():
            print(p.stdout.strip())
        if p.stderr.strip():
            print(f"[stderr] {p.stderr.strip()[:500]}")
        if p.returncode != 0:
            print(f"[ABORT] {name} failed with exit {p.returncode}")
            append_log(log_path, log_entry)
            return False, log_entry
        append_log(log_path, log_entry)
        return True, log_entry
    except Exception as e:
        dur = round(time.time() - t0, 2)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "step": name,
            "status": "failed",
            "duration": dur,
            "records_added": 0,
            "records_reviewed": 0,
            "errors": [{"step": name, "message": str(e)}],
        }
        append_log(log_path, log_entry)
        print(f"[ABORT] {name} exception: {e}")
        return False, log_entry


def append_log(log_path, entry):
    logs = []
    if log_path.exists():
        try:
            logs = json.load(open(log_path, encoding="utf-8"))
        except Exception:
            logs = []
    logs.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-infographic", action="store_true")
    ap.add_argument("--no-phase-check", action="store_true")
    ap.add_argument("--schedule", action="store_true", help="print scheduling command")
    args = ap.parse_args()

    if args.schedule:
        if os.name == "nt":
            print("Windows Task Scheduler command (run daily at 02:00):")
            print(f'schtasks /Create /TN "CIVID Daily Update" /TR "\\"{sys.executable}\\" \\"{SCRIPTS / "run_pipeline.py"}\\"\"" /SC DAILY /ST 02:00 /F')
        else:
            print("Cron job (run daily at 02:00):")
            print(f"0 2 * * * {sys.executable} {SCRIPTS / 'run_pipeline.py'}")
        return

    OUTPUT.mkdir(parents=True, exist_ok=True)
    log_path = OUTPUT / "run_log.json"

    print("=== CIVID Full Pipeline ===")
    t0 = time.time()

    steps = [
        ("validate", [sys.executable, str(SCRIPTS / "validate_dataset.py")]),
        ("renumber", [sys.executable, str(SCRIPTS / "renumber_records.py")]),
        ("news", [sys.executable, str(SCRIPTS / "generate_news_intelligence.py")]),
        ("export", [sys.executable, str(SCRIPTS / "build_exports.py")]),
        ("dashboard", [sys.executable, str(SCRIPTS / "generate_html_dashboard.py")]),
    ]
    if not args.no_infographic:
        steps.append(("infographic", [sys.executable, str(SCRIPTS / "infographic.py")]))
    if not args.no_phase_check:
        steps.append(("phase_orchestrator", [sys.executable, str(SCRIPTS / "phase_orchestrator.py"), "--no-refresh"]))

    failed = False
    for name, cmd in steps:
        ok, entry = run_step(name, cmd, log_path)
        if not ok:
            if name == "infographic":
                print("[warn] Infographic generation failed (matplotlib may not be installed). Continuing...")
                continue
            failed = True
            break

    total_dur = round(time.time() - t0, 2)
    added = 0
    reviewed = 0
    try:
        summary_data = json.load(open(EXPORTS / "summary.json", encoding="utf-8"))
        added = summary_data.get("totals", {}).get("events", 0)
        reviewed = summary_data.get("totals", {}).get("events_verified", 0)
    except Exception:
        pass
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "step": "pipeline_summary",
        "status": "failed" if failed else "success",
        "duration": total_dur,
        "records_added": added,
        "records_reviewed": reviewed,
        "errors": [],
    }
    append_log(log_path, summary)

    if failed:
        print(f"[ABORT] Pipeline failed after {total_dur}s. Check logs at output/run_log.json")
        sys.exit(1)
    else:
        print(f"[ok] Pipeline completed successfully in {total_dur}s")
        sys.exit(0)


if __name__ == "__main__":
    main()
