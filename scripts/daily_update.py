"""
CIVID Daily Update Script
==========================
Fetches new humanitarian situation reports from the ReliefWeb API (official,
public, no API key required) for the countries/phases defined in PHASES below,
and writes them to a STAGING file for human review — it never auto-merges
into the verified events.csv/persons.csv files.

Why ReliefWeb: it's an official UN OCHA-run aggregator API designed for
exactly this kind of programmatic access (see https://reliefweb.int/help/api).
It is not screen-scraping — it's a supported, documented API.

Run manually:
    conda activate civid
    python scripts/daily_update.py

Run automatically: see the "Task Scheduler" section in README_AUTOMATION.md
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error, parse

# ---- Configuration ----------------------------------------------------

RELIEFWEB_API = "https://api.reliefweb.int/v1/reports"
APPNAME = "civid-dataset-research"  # ReliefWeb asks for an appname identifier

PHASES = {
    "phase1_palestine": {
        "country": "occupied Palestinian territory",
        "phase": 1,
    },
    "phase2_sudan": {
        "country": "Sudan",
        "phase": 2,
    },
}

ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = ROOT / "data" / "staging"
STAGING_FILE = STAGING_DIR / "pending_review.csv"

STAGING_FIELDS = [
    "staging_id", "fetched_at", "phase", "country",
    "report_title", "report_date", "source_name", "source_url",
    "citation_text", "verification_status", "confidence_level", "notes",
]


# ---- Fetch logic -------------------------------------------------------

def fetch_reliefweb_reports(country: str, limit: int = 10) -> list[dict]:
    """Query the ReliefWeb API for recent reports mentioning a given country."""
    query = {
        "appname": APPNAME,
        "profile": "list",
        "preset": "latest",
        "slim": 1,
        "limit": limit,
        "filter[field]": "country",
        "filter[value]": country,
    }
    url = f"{RELIEFWEB_API}?{parse.urlencode(query)}"

    try:
        with request.urlopen(url, timeout=20) as resp:
            data = json.load(resp)
    except error.URLError as e:
        print(f"[warn] Could not reach ReliefWeb API for '{country}': {e}")
        return []

    results = []
    for item in data.get("data", []):
        fields = item.get("fields", {})
        results.append({
            "title": fields.get("title", "").strip(),
            "date": fields.get("date", {}).get("original", "")[:10],
            "url": fields.get("url_alias") or fields.get("url", ""),
            "source": ", ".join(
                s.get("name", "") for s in fields.get("source", [])
            ) or "ReliefWeb",
        })
    return results


def load_existing_staging_ids() -> set:
    if not STAGING_FILE.exists():
        return set()
    with open(STAGING_FILE, newline="", encoding="utf-8") as f:
        return {row["staging_id"] for row in csv.DictReader(f)}


def append_to_staging(rows: list[dict]):
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = STAGING_FILE.exists()
    with open(STAGING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STAGING_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ---- Main ----------------------------------------------------------------

def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing_ids = load_existing_staging_ids()
    new_rows = []

    for phase_dir, cfg in PHASES.items():
        print(f"Fetching latest ReliefWeb reports for {cfg['country']} (phase {cfg['phase']})...")
        reports = fetch_reliefweb_reports(cfg["country"])

        for r in reports:
            staging_id = f"{phase_dir}-{r['date']}-{abs(hash(r['title'])) % 100000}"
            if staging_id in existing_ids:
                continue  # already staged in a previous run

            new_rows.append({
                "staging_id": staging_id,
                "fetched_at": now,
                "phase": cfg["phase"],
                "country": cfg["country"],
                "report_title": r["title"],
                "report_date": r["date"],
                "source_name": r["source"],
                "source_url": r["url"],
                "citation_text": "",  # human fills in exact citation after reading the report
                "verification_status": "unverified",  # NEVER auto-mark as verified
                "confidence_level": "low",             # NEVER auto-mark as high
                "notes": "Auto-fetched candidate — requires human review before merging into events.csv",
            })

    if new_rows:
        append_to_staging(new_rows)
        print(f"[ok] Added {len(new_rows)} new candidate reports to {STAGING_FILE}")
        print("     These are NOT verified and NOT part of the main dataset yet.")
        print("     Review data/staging/pending_review.csv and manually promote entries")
        print("     into the appropriate events.csv following the normal citation rules.")
    else:
        print("[ok] No new reports found since last run.")


if __name__ == "__main__":
    main()
