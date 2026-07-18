#!/usr/bin/env python3
"""CIVID real-time refresh orchestrator.

Runs the full pipeline in the correct order so the HTML dashboard (which reads
exports/) always reflects the current data/:

    1. validate_dataset.py      (abort if errors)
    2. renumber_records.py      (idempotent gap-free IDs)
    3. generate_news_intelligence.py
    4. build_exports.py          (writes exports/*.csv + .json + dashboard html data)
    5. generate_html_dashboard.py

Run:  python scripts/refresh.py
"""
from __future__ import annotations
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    p = subprocess.run([sys.executable, *cmd], cwd=REPO, capture_output=True, text=True)
    print(p.stdout.strip())
    if p.stderr.strip():
        print("[stderr]", p.stderr.strip())
    if p.returncode != 0:
        print(f"[ABORT] {cmd} failed with exit {p.returncode}")
        raise SystemExit(1)


def main():
    print("=== CIVID refresh (validate -> renumber -> news -> export -> dashboard) ===")
    run(["scripts/validate_dataset.py"])
    run(["scripts/renumber_records.py"])
    run(["scripts/generate_news_intelligence.py"])
    run(["scripts/build_exports.py"])
    run(["scripts/generate_html_dashboard.py"])
    print("[ok] Dashboard refreshed. Open exports/civid_dashboard.html (or serve via scripts/serve_dashboard.py).")


if __name__ == "__main__":
    main()
