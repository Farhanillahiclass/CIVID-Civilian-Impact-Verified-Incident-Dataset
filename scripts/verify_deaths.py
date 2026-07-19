#!/usr/bin/env python3
"""Apply the funeral/burial/memorial death-verification rule to a leader record.

Rule (docs/death_verification_policy.md): if a major reliable outlet reports funeral,
burial, or memorial rites for a person described as 'late'/'slain'/'deceased', and no
equally reliable source contradicts it, then:
  - death_status = "dead"
  - burial_status = "buried" (if burial reported) else "not buried"
  - verification_status = "verified"
  - last_checked = <confirmation date>
  - source_set = <all supporting source URLs, pipe-separated>
  - if previously unverified, append a changelog entry.

This script ONLY promotes when real source URLs are passed on the command line. It never
infers or fabricates. If no sources are given, it refuses.

Run:
  python scripts/verify_deaths.py LDR-025 \
      --date 2026-07-19 \
      --buried \
      --source "https://www.reuters.com/..." \
      --source "https://apnews.com/..."
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADERS = os.path.join(REPO, "data", "leaders.csv")
CHANGELOG = os.path.join(REPO, "CHANGELOG_autopush.md")


def load_rows():
    with open(LEADERS, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def save_rows(rows):
    fields = list(rows[0].keys())
    # ensure new columns exist
    for col in ("burial_status", "last_checked", "source_set"):
        if col not in fields:
            fields.append(col)
            for r in rows:
                r.setdefault(col, "")
    with open(LEADERS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("leader_id")
    ap.add_argument("--date", required=True, help="confirmation date YYYY-MM-DD")
    ap.add_argument("--buried", action="store_true", help="burial rites reported")
    ap.add_argument("--source", action="append", default=[], help="supporting source URL (repeatable)")
    args = ap.parse_args()

    if not args.source:
        print("[ABORT] No --source URL provided. The death-verification rule requires at "
              "least one reliable source that was actually read. Refusing to promote.")
        raise SystemExit(1)

    rows = load_rows()
    target = next((r for r in rows if r["leader_id"] == args.leader_id), None)
    if target is None:
        print(f"[error] {args.leader_id} not found.")
        raise SystemExit(1)

    was_unverified = (target.get("verification_status") or "").strip().lower() == "unverified"

    target["death_status"] = "dead"
    target["burial_status"] = "buried" if args.buried else "not buried"
    target["verification_status"] = "verified"
    target["confidence_level"] = "high"
    target["last_checked"] = args.date
    target["source_set"] = "|".join(args.source)
    target["needs_review"] = "false"
    prev = target.get("verification_status")
    target["notes"] = (target.get("notes") or "").strip().rstrip(";") + \
        f" [Death verified via funeral/burial/memorial rule {args.date}; sources: {len(args.source)}]."

    save_rows(rows)

    if was_unverified:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        line = (f"\n## {stamp}\n- DEATH VERIFICATION (funeral/burial rule): {args.leader_id} "
                f"promoted unverified -> verified (death_status=dead, burial_status="
                f"{target['burial_status']}, last_checked={args.date}, sources={len(args.source)}).\n")
        with open(CHANGELOG, "a", encoding="utf-8") as f:
            f.write(line)

    print(f"[ok] {args.leader_id} -> death_status=dead, burial_status={target['burial_status']}, "
          f"verification_status=verified, last_checked={args.date}")


if __name__ == "__main__":
    raise SystemExit(main())
