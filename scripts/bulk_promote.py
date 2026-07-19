"""
CIVID Bulk Promote Script
============================
Moves ALL entries currently in data/staging/pending_review.csv directly into
the correct phase's events.csv and sources.csv — in ONE command, no per-row
prompts. Then, automatically commits and pushes the updates to GitHub.

IMPORTANT — what this does and doesn't do:
  - It does NOT read the actual source content or confirm any fact.
  - Every row it adds is marked verification_status = "unverified" and
    confidence_level = "low", with a note flagging it as auto-promoted.
  - This is intentional: the script cannot know if a dataset title actually
    matches a citable, accurate fact. Marking everything "verified" would be
    honest and would break the whole point of this dataset.

Use this when you want speed and are okay reviewing/upgrading confidence
levels later (in the dashboard or by hand), rather than reviewing each row
before it's added.

Usage:
    conda activate civid
    python scripts/bulk_promote.py
"""

import csv
import uuid
from pathlib import Path
import git  # Requires 'pip install GitPython'

ROOT = Path(__file__).resolve().parent.parent
STAGING_FILE = ROOT / "data" / "staging" / "pending_review.csv"

PHASE_DIRS = {
     1: ROOT / "data" / "phase1_palestine",
     2: ROOT / "data" / "phase2_sudan",
     3: ROOT / "data" / "phase3_iran",
     4: ROOT / "data" / "phase4_additional",
 }
 PHASE_COUNTRY = {1: "Palestine", 2: "Sudan", 3: "Iran", 4: "Yemen"}
 PHASE_CONFLICT = {1: "Israeli-Palestinian conflict", 2: "Sudanese civil conflict", 3: "Iran-Israel Twelve-Day War", 4: "Yemen conflict (Red Sea crisis)"}

EVENTS_FIELDS = [
    "record_id", "phase", "country", "conflict_name", "event_id", "event_date",
    "location", "location_type", "source_id", "fatalities", "injuries",
    "missing", "verification_status", "confidence_level", "notes",
]
SOURCES_FIELDS = [
    "source_id", "source_name", "source_url", "source_type",
    "source_date", "citation_text", "reliability_score",
]


def get(row, *keys, default=""):
    for k in keys:
        if row.get(k):
            return row[k]
    return default


def load_staging_rows():
    if not STAGING_FILE.exists():
        return []
    with open(STAGING_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def next_event_id(events_csv: Path) -> int:
    if not events_csv.exists():
        return 1
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
    return (max(nums) + 1) if nums else 1


def append_row(csv_path: Path, fieldnames, row):
    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main():
    rows = load_staging_rows()
    if not rows:
        print("No staged entries to promote.")
        return

    print(f"Found {len(rows)} staged entries. Bulk-promoting as UNVERIFIED / LOW confidence.\n")

    counters = {1: None, 2: None}  # lazy-init next event id per phase

    added = 0
    for row in rows:
        try:
            phase = int(row.get("phase", 0))
        except ValueError:
            phase = 0
        phase_dir = PHASE_DIRS.get(phase)
        if not phase_dir:
            print(f"[skip] '{get(row, 'title', 'report_title', 'dataset_title')}' — unknown phase '{row.get('phase')}'")
            continue

        events_csv = phase_dir / "events.csv"
        sources_csv = phase_dir / "sources.csv"

        if counters[phase] is None:
            counters[phase] = next_event_id(events_csv)
        event_num = counters[phase]
        counters[phase] += 1

        title = get(row, "title", "report_title", "dataset_title")
        url = get(row, "url", "source_url", "dataset_url")
        org = get(row, "org_or_source", "source_name", "organization")
        date = get(row, "date_or_modified", "report_date", "dataset_modified")

        source_id = f"SRC-{uuid.uuid4().hex[:8]}"
        record_id = f"REC-{uuid.uuid4().hex[:8]}"
        event_id = f"EVT-{event_num:03d}"

        append_row(sources_csv, SOURCES_FIELDS, {
            "source_id": source_id,
            "source_name": org,
            "source_url": url,
            "source_type": row.get("source_system", "unknown"),
            "source_date": date,
            "citation_text": title,
            "reliability_score": "",
        })

        append_row(events_csv, EVENTS_FIELDS, {
            "record_id": record_id,
            "phase": phase,
            "country": PHASE_COUNTRY.get(phase, ""),
            "conflict_name": PHASE_CONFLICT.get(phase, ""),
            "event_id": event_id,
            "event_date": date,
            "location": "",
            "location_type": "",
            "source_id": source_id,
            "fatalities": "",
            "injuries": "",
            "missing": "",
            "verification_status": "unverified",
            "confidence_level": "low",
            "notes": f"Auto-promoted from staging without individual review. "
                     f"Title as fetched: '{title}'. Open {url} to confirm facts and "
                     f"upgrade verification_status/confidence_level once reviewed.",
        })

        print(f"[added] {event_id} — {title[:70]}")
        added += 1

    # Clear the staging file now that everything's been moved
    with open(STAGING_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()

    print(f"\n[ok] Promoted {added} entries. Staging queue cleared.")
    print("[reminder] All of these are marked 'unverified' / 'low' confidence.")
    print("           Open each source_url in sources.csv when you get a chance,")
    print("           fill in fatalities/injuries/location, and upgrade the status.")

    # ---- Automatic Git Commit and Push ----
    try:
        print("\n[git] Initializing repository synchronization...")
        repo = git.Repo(ROOT)
        
        # Stage all updated dataset tracks and staging file
        repo.git.add(A=True)
        
        # Commit changes with count details
        commit_message = f"Bulk-add: Promoted {added} unverified data candidates to production tracks"
        repo.index.commit(commit_message)
        
        # Push upstream
        origin = repo.remote(name="origin")
        origin.push()
        print(f"[git ok] Successfully synced to GitHub repository via commit: '{commit_message}'")
        
    except Exception as e:
        print(f"\n[git error] Automating remote synchronization failed: {e}")
        print("Please check your local Git user identity settings or upstream repository access tokens.")


if __name__ == "__main__":
    main()