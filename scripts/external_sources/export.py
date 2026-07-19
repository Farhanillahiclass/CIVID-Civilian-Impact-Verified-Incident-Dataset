"""
Export layer. Stdlib-only.
Writes unified CSV + JSON, a per-run changelog, and a human-review queue
for partial/uncertain records. Mirrors CIVID's staging convention:
records are written to data/staging/ only; nothing is auto-promoted.

Also writes the Pass-2 profile outputs (person profiles, famous candidates,
image metadata, profile review queue).
"""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT

STAGING = ROOT / "data" / "staging"
RECORDS_CSV = STAGING / "external_records.csv"
RECORDS_JSON = STAGING / "external_records.json"
CHANGELOG = STAGING / "external_changelog.csv"
REVIEW_QUEUE = STAGING / "external_review_queue.csv"
PROFILES_JSON = STAGING / "external_person_profiles.json"
FAMOUS_JSON = STAGING / "external_famous_candidates.json"
IMAGES_JSON = STAGING / "external_image_metadata.json"
PROFILE_REVIEW_JSON = STAGING / "external_profile_review.json"

CSV_FIELDS = [
    "record_id", "source_name", "source_type", "source_url", "source_date",
    "source_license", "source_access_method", "title", "subtitle", "author",
    "publication_date", "section", "tags", "categories", "summary",
    "full_text", "image_url", "image_caption", "image_license", "page_id",
    "revision_id", "language", "extraction_status", "confidence_score",
    "notes", "checksum", "duplicate_flag",
]


def _cell(v):
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    if v is None:
        return ""
    return v


def export(records: list[dict], run_meta: dict):
    STAGING.mkdir(parents=True, exist_ok=True)

    # Unified CSV + JSON (all records)
    with open(RECORDS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow({k: _cell(r.get(k)) for k in CSV_FIELDS})
    with open(RECORDS_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # Human-review queue (partial / failed / low confidence)
    review = [r for r in records if r.get("extraction_status") in ("partial", "failed", "queued_review")
              or r.get("confidence_score", 1) < 0.6]
    if review:
        with open(REVIEW_QUEUE, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            w.writeheader()
            for r in review:
                w.writerow({k: _cell(r.get(k)) for k in CSV_FIELDS})

    # Changelog (one row per run)
    clog_exists = CHANGELOG.exists()
    with open(CHANGELOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not clog_exists:
            w.writerow(["run_at", "source", "status", "records", "review", "notes"])
        w.writerow([
            run_meta.get("run_at"),
            run_meta.get("source", "all"),
            run_meta.get("status", "ok"),
            len(records),
            len(review),
            run_meta.get("notes", ""),
        ])


def export_profiles(profile_outputs: dict):
    STAGING.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_JSON, "w", encoding="utf-8") as f:
        json.dump(profile_outputs.get("person_profiles", []), f, ensure_ascii=False, indent=2)
    with open(FAMOUS_JSON, "w", encoding="utf-8") as f:
        json.dump(profile_outputs.get("famous_candidates", []), f, ensure_ascii=False, indent=2)
    with open(IMAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(profile_outputs.get("images", []), f, ensure_ascii=False, indent=2)
    with open(PROFILE_REVIEW_JSON, "w", encoding="utf-8") as f:
        json.dump(profile_outputs.get("review", []), f, ensure_ascii=False, indent=2)


def log_failure(source: str, message: str):
    STAGING.mkdir(parents=True, exist_ok=True)
    clog_exists = CHANGELOG.exists()
    with open(CHANGELOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not clog_exists:
            w.writerow(["run_at", "source", "status", "records", "review", "notes"])
        w.writerow([
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            source, "failed", 0, 0, message,
        ])
