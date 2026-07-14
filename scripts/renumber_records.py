#!/usr/bin/env python3
"""CIVID record renumbering (standard-library only).

Re-generates the row primary key of each phase's events / persons / famous_victims
tables as a gap-free sequential sequence (1..N) per table, while:

- preserving the ORIGINAL id in a `legacy_record_id` column (provenance rule),
- keeping the business key `event_id` STABLE (it is the cross-table link, never renumbered),
- remapping `famous_victims.person_record_id` when persons are renumbered (FK-safe),
- writing a human-readable change log to CHANGELOG_renumber.md.

Idempotent: `legacy_record_id` is only written the first time (kept thereafter), so
re-running keeps the true original id.

Run:  python scripts/renumber_records.py            (apply)
      python scripts/renumber_records.py --dry-run  (report only)
"""
from __future__ import annotations
import csv
import os
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
PHASES = ["phase1_palestine", "phase2_sudan", "phase3_iran", "phase4_additional"]

# table file -> primary key column
TABLES = {
    "events.csv": "record_id",
    "persons.csv": "record_id",
    "famous_victims.csv": "famous_id",
}

dry_run = "--dry-run" in sys.argv
log_lines: list[str] = []


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        r = csv.DictReader(fh)
        return list(r), (r.fieldnames or [])


def write_rows(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def renumber_table(path, pk):
    if not os.path.exists(path):
        return None
    rows, fieldnames = read_rows(path)
    if not rows:
        return {"rows": 0, "map": {}}
    # ensure legacy column present right after pk
    if "legacy_record_id" not in fieldnames:
        new_fields = [pk, "legacy_record_id"] + [f for f in fieldnames if f != pk]
    else:
        new_fields = fieldnames
    id_map = {}
    for i, row in enumerate(rows, start=1):
        old = (row.get(pk) or "").strip()
        if not (row.get("legacy_record_id") or "").strip():
            row["legacy_record_id"] = old  # first-time provenance capture
        new = str(i)
        row[pk] = new
        id_map[old] = new
    if not dry_run:
        write_rows(path, rows, new_fields)
    return {"rows": len(rows), "map": id_map}


def main():
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log_lines.append(f"# CIVID Record Renumbering Change Log\n")
    log_lines.append(f"Run: {stamp} {'(DRY RUN)' if dry_run else ''}\n")
    log_lines.append("event_id is the stable cross-table key and is never renumbered. "
                     "Row primary keys are renumbered 1..N per table; the original id is kept "
                     "in `legacy_record_id`.\n")

    for phase in PHASES:
        pdir = os.path.join(DATA, phase)
        if not os.path.isdir(pdir):
            continue
        # persons first so we can remap famous_victims.person_record_id
        persons_res = renumber_table(os.path.join(pdir, "persons.csv"), "record_id")
        events_res = renumber_table(os.path.join(pdir, "events.csv"), "record_id")

        # famous_victims: renumber pk AND remap person_record_id via persons map
        fpath = os.path.join(pdir, "famous_victims.csv")
        famous_res = None
        if os.path.exists(fpath):
            rows, fieldnames = read_rows(fpath)
            if rows:
                pmap = persons_res["map"] if persons_res else {}
                for row in rows:
                    old_pr = (row.get("person_record_id") or "").strip()
                    if old_pr and old_pr in pmap:
                        row["person_record_id"] = pmap[old_pr]
                famous_res = renumber_table(fpath, "famous_id")
            else:
                famous_res = {"rows": 0, "map": {}}

        log_lines.append(f"\n## {phase}")
        for name, res in (("events", events_res), ("persons", persons_res), ("famous_victims", famous_res)):
            if res is None:
                continue
            log_lines.append(f"- {name}: {res['rows']} row(s) renumbered 1..{res['rows']}")
            for old, new in list(res.get("map", {}).items())[:200]:
                if old != new:
                    log_lines.append(f"    - {old} -> {new}")

    out = os.path.join(REPO, "CHANGELOG_renumber.md")
    if not dry_run:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print(f"\n[{'dry-run' if dry_run else 'ok'}] change log {'would be' if dry_run else ''} written to {out}")


if __name__ == "__main__":
    main()
