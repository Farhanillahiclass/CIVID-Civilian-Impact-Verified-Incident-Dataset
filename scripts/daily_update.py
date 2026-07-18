"""
CIVID Daily Update Script (HDX + ReliefWeb multi-source)
===========================================================
PHASE-AWARE: extracts candidates for the CURRENT frontier phase (read from
data/staging/current_phase.txt). Defaults to phase1_palestine if the state
file is absent. To add a new country/phase, add it to the PHASES map below
AND to data/staging/current_phase.txt via scripts/phase_orchestrator.py.

Sources used:
1. HDX (Humanitarian Data Exchange) CKAN API — NO registration required,
   run directly by OCHA. Primary source.
2. ReliefWeb API — used as a secondary attempt; requires a pre-approved
   appname. If not yet approved, this source is skipped automatically
   without breaking the run.

This script NEVER writes to the verified events.csv/persons.csv files.
It only appends candidate rows to data/staging/pending_review.csv, marked
unverified/low-confidence. Use scripts/promote_entry.py after you've
manually reviewed a row and confirmed it against the real source.

Run manually:
    python scripts/daily_update.py
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error, parse

# ---- Configuration (all supported phases) ----------------------------

HDX_API = "https://data.humdata.org/api/3/action/package_search"
RELIEFWEB_API = "https://api.reliefweb.int/v2/reports"
RELIEFWEB_APPNAME = "civid-dataset-research"  # update once approved

# Phase-aware query map. Add new phases here as the project scope grows.
PHASES = {
    "phase1_palestine": {
        "hdx_query": "Palestine OR Gaza OR oPt",
        "reliefweb_country": "occupied Palestinian territory",
        "phase": 1,
    },
    "phase2_sudan": {
        "hdx_query": "Sudan",
        "reliefweb_country": "Sudan",
        "phase": 2,
    },
    "phase3_iran": {
        "hdx_query": "Iran OR Israel",
        "reliefweb_country": "Iran",
        "phase": 3,
    },
    "phase4_additional": {
        "hdx_query": "Yemen OR Red Sea",
        "reliefweb_country": "Yemen",
        "phase": 4,
    },
}

CURRENT_PHASE_FILE = Path(__file__).resolve().parent.parent / "data" / "staging" / "current_phase.txt"


def current_phase_key() -> str:
    """Return the phase key for the active frontier (from state file)."""
    if CURRENT_PHASE_FILE.exists():
        try:
            idx = int(CURRENT_PHASE_FILE.read_text(encoding="utf-8").strip())
            for key, cfg in PHASES.items():
                if cfg["phase"] == idx:
                    return key
        except Exception:
            pass
    return "phase1_palestine"

ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = ROOT / "data" / "staging"
STAGING_FILE = STAGING_DIR / "pending_review.csv"

STAGING_FIELDS = [
    "staging_id", "fetched_at", "phase", "source_system", "query_used",
    "title", "date_or_modified", "org_or_source", "url",
    "citation_text", "verification_status", "confidence_level", "notes",
]

HEADERS = {
    "User-Agent": "civid-dataset-research/1.0 (non-commercial humanitarian research)",
    "Accept": "application/json",
}


# ---- Source 1: HDX (no registration needed) -----------------------------

def fetch_hdx_datasets(query: str, rows: int = 8) -> list[dict]:
    params = {"q": query, "rows": rows, "sort": "metadata_modified desc"}
    url = f"{HDX_API}?{parse.urlencode(params)}"
    req = request.Request(url, headers=HEADERS)
    try:
        with request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except (error.HTTPError, error.URLError, json.JSONDecodeError) as e:
        print(f"[warn] HDX fetch failed for '{query}': {e}")
        return []

    if not data.get("success"):
        print(f"[warn] HDX API reported failure for '{query}'")
        return []

    out = []
    for pkg in data.get("result", {}).get("results", []):
        out.append({
            "title": pkg.get("title", "").strip(),
            "date": (pkg.get("metadata_modified") or "")[:10],
            "org": (pkg.get("organization") or {}).get("title", "Unknown org"),
            "url": f"https://data.humdata.org/dataset/{pkg.get('name', '')}",
        })
    return out


# ---- Source 2: ReliefWeb (needs approved appname) ------------------------

def fetch_reliefweb_reports(country: str, limit: int = 8) -> list[dict]:
    params = {
        "appname": RELIEFWEB_APPNAME, "profile": "list", "preset": "latest",
        "slim": 1, "limit": limit,
        "filter[field]": "country", "filter[value]": country,
    }
    url = f"{RELIEFWEB_API}?{parse.urlencode(params)}"
    req = request.Request(url, headers=HEADERS)
    try:
        with request.urlopen(req, timeout=20) as resp:
            if resp.status != 200:
                print(f"[info] ReliefWeb not available yet for '{country}' "
                      f"(appname likely unapproved) — skipping this source.")
                return []
            data = json.load(resp)
    except (error.HTTPError, error.URLError, json.JSONDecodeError):
        print(f"[info] ReliefWeb source unavailable for '{country}' — skipping.")
        return []

    out = []
    for item in data.get("data", []):
        fields = item.get("fields", {})
        out.append({
            "title": fields.get("title", "").strip(),
            "date": fields.get("date", {}).get("original", "")[:10],
            "org": ", ".join(s.get("name", "") for s in fields.get("source", [])) or "ReliefWeb",
            "url": fields.get("url_alias") or fields.get("url", ""),
        })
    return out


# ---- Staging helpers -------------------------------------------------------

def load_existing_staging_ids() -> set:
    if not STAGING_FILE.exists():
        return set()
    with open(STAGING_FILE, newline="", encoding="utf-8") as f:
        return {row["staging_id"] for row in csv.DictReader(f)}


def append_to_staging(rows: list[dict]):
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    # Detect a stale/mismatched header from an older script version and
    # safely archive it instead of silently corrupting the column layout.
    if STAGING_FILE.exists():
        with open(STAGING_FILE, newline="", encoding="utf-8") as f:
            existing_header = next(csv.reader(f), [])
        if existing_header and existing_header != STAGING_FIELDS:
            backup = STAGING_DIR / f"pending_review_old_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            STAGING_FILE.rename(backup)
            print(f"[info] Old staging file had a different format — archived to {backup.name}, starting fresh.")

    file_exists = STAGING_FILE.exists()
    with open(STAGING_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=STAGING_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ---- Main -------------------------------------------------------------------

def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing_ids = load_existing_staging_ids()
    new_rows = []

    # Extract only for the CURRENT frontier phase (phase-aware).
    phase_dir = current_phase_key()
    cfg = PHASES[phase_dir]
    print(f"\n=== Phase {cfg['phase']} ({phase_dir}) [active frontier] ===")

    print(f"[HDX] query: {cfg['hdx_query']}")
    for d in fetch_hdx_datasets(cfg["hdx_query"]):
        sid = f"{phase_dir}-hdx-{d['date']}-{abs(hash(d['title'])) % 100000}"
        if sid in existing_ids:
            continue
        new_rows.append({
            "staging_id": sid, "fetched_at": now, "phase": cfg["phase"],
            "source_system": "HDX", "query_used": cfg["hdx_query"],
            "title": d["title"], "date_or_modified": d["date"],
            "org_or_source": d["org"], "url": d["url"],
            "citation_text": "", "verification_status": "unverified",
            "confidence_level": "low",
            "notes": "Dataset-level metadata from HDX — open the URL and extract "
                     "a specific citable fact before promoting.",
        })

    print(f"[ReliefWeb] country: {cfg['reliefweb_country']}")
    for r in fetch_reliefweb_reports(cfg["reliefweb_country"]):
        sid = f"{phase_dir}-rw-{r['date']}-{abs(hash(r['title'])) % 100000}"
        if sid in existing_ids:
            continue
        new_rows.append({
            "staging_id": sid, "fetched_at": now, "phase": cfg["phase"],
            "source_system": "ReliefWeb", "query_used": cfg["reliefweb_country"],
            "title": r["title"], "date_or_modified": r["date"],
            "org_or_source": r["org"], "url": r["url"],
            "citation_text": "", "verification_status": "unverified",
            "confidence_level": "low",
            "notes": "Report from ReliefWeb — review before promoting.",
        })

    if new_rows:
        append_to_staging(new_rows)
        print(f"\n[ok] Added {len(new_rows)} new candidates to {STAGING_FILE}")
        print("     Review each, then run: python scripts/promote_entry.py <staging_id>")
    else:
        print("\n[ok] No new candidates found since last run.")


if __name__ == "__main__":
    main()
