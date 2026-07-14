"""
CIVID Promote Entry Script
============================
This is the tool you run AFTER you've manually reviewed a candidate row in
data/staging/pending_review.csv against its real source. It asks you a few
questions (interactively) and then writes a properly-formatted verified row
directly into the correct phase's events.csv — so you never have to hand-edit
the CSV yourself.

It does NOT invent any facts. Every field you're asked for must come from
what you actually read in the source. If you don't know a value, just press
Enter to leave it blank — never guess.

Usage:
    conda activate civid
    python scripts/promote_entry.py <staging_id>

Example:
    python scripts/promote_entry.py phase2_sudan-hdx-2026-07-01-48213

To see all pending staging IDs first:
    python scripts/promote_entry.py --list
"""

import csv
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING_FILE = ROOT / "data" / "staging" / "pending_review.csv"

PHASE_DIRS = {
    1: ROOT / "data" / "phase1_palestine",
    2: ROOT / "data" / "phase2_sudan",
}

EVENTS_FIELDS = [
    "record_id", "phase", "country", "conflict_name", "event_id", "event_date",
    "location", "location_type", "source_id", "fatalities", "injuries",
    "missing", "verification_status", "confidence_level", "notes",
]

SOURCES_FIELDS = [
    "source_id", "source_name", "source_url", "source_type",
    "source_date", "citation_text", "reliability_score",
]


def load_staging_rows() -> list[dict]:
    if not STAGING_FILE.exists():
        return []
    with open(STAGING_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def next_event_id(events_csv: Path) -> str:
    if not events_csv.exists():
        return "EVT-001"
    with open(events_csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    nums = []
    for r in rows:
        eid = r.get("event_id", "")
        if eid.startswith("EVT-"):
            try:
                nums.append(int(eid.split("-")[1]))
            except ValueError:
                pass
    return f"EVT-{(max(nums) + 1) if nums else 1:03d}"


def append_row(csv_path: Path, fieldnames: list[str], row: dict):
    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def remove_from_staging(staging_id: str):
    rows = load_staging_rows()
    remaining = [r for r in rows if r["staging_id"] != staging_id]
    if not STAGING_FILE.exists():
        return
    with open(STAGING_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        writer.writeheader()
        writer.writerows(remaining)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--list":
        rows = load_staging_rows()
        if not rows:
            print("No pending entries in staging.")
            return
        for r in rows:
            print(f"  {r['staging_id']}  |  phase {r['phase']}  |  {r['title'][:60]}")
        return

    staging_id = sys.argv[1]
    rows = load_staging_rows()
    match = next((r for r in rows if r["staging_id"] == staging_id), None)

    if not match:
        print(f"[error] staging_id '{staging_id}' not found. Run with --list to see options.")
        sys.exit(1)

    phase = int(match["phase"])
    phase_dir = PHASE_DIRS.get(phase)
    if not phase_dir:
        print(f"[error] Unknown phase {phase} — this script only supports Palestine (1) and Sudan (2).")
        sys.exit(1)

    print(f"\n--- Reviewing: {match['title']} ---")
    print(f"Source: {match['org_or_source']}")
    print(f"URL: {match['url']}")
    print("\nOpen that URL now and confirm the facts before continuing.")
    confirm = ask("Have you read and verified the source? (yes/no)", "no")
    if confirm.lower() != "yes":
        print("Aborted — please review the source first.")
        sys.exit(0)

    print("\nEnter event details (leave blank if unknown — never guess):")
    country = ask("Country", "Palestine" if phase == 1 else "Sudan")
    conflict_name = ask("Conflict name", "Israel-Palestine conflict" if phase == 1 else "Sudan civil conflict")
    event_date = ask("Event date (YYYY-MM-DD)", match.get("date_or_modified", ""))
    location = ask("Location")
    location_type = ask("Location type (e.g. city, camp, hospital)")
    fatalities = ask("Fatalities (number, blank if unknown)")
    injuries = ask("Injuries (number, blank if unknown)")
    missing = ask("Missing (number, blank if unknown)")
    verification_status = ask("Verification status (verified/estimated/unverified/disputed)", "verified")
    confidence_level = ask("Confidence level (high/medium/low)", "medium")
    notes = ask("Notes")
    citation_text = ask("Exact citation text (quote/paraphrase what the source states)")
    reliability_score = ask("Source reliability score 0.0-1.0", "0.90")

    events_csv = phase_dir / "events.csv"
    sources_csv = phase_dir / "sources.csv"

    event_id = next_event_id(events_csv)
    source_id = f"SRC-{uuid.uuid4().hex[:8]}"
    record_id = f"REC-{uuid.uuid4().hex[:8]}"

    append_row(sources_csv, SOURCES_FIELDS, {
        "source_id": source_id,
        "source_name": match["org_or_source"],
        "source_url": match["url"],
        "source_type": match["source_system"],
        "source_date": match.get("date_or_modified", ""),
        "citation_text": citation_text,
        "reliability_score": reliability_score,
    })

    append_row(events_csv, EVENTS_FIELDS, {
        "record_id": record_id,
        "phase": phase,
        "country": country,
        "conflict_name": conflict_name,
        "event_id": event_id,
        "event_date": event_date,
        "location": location,
        "location_type": location_type,
        "source_id": source_id,
        "fatalities": fatalities,
        "injuries": injuries,
        "missing": missing,
        "verification_status": verification_status,
        "confidence_level": confidence_level,
        "notes": notes,
    })

    remove_from_staging(staging_id)

    print(f"\n[ok] Added {event_id} to {events_csv}")
    print(f"[ok] Added source {source_id} to {sources_csv}")
    print(f"[ok] Removed '{staging_id}' from staging queue")
    print("\nDon't forget to: git add . && git commit -m 'Add verified event' && git push")


if __name__ == "__main__":
    main()
