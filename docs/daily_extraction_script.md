# CIVID — Daily Extraction Script Design

Implemented in `scripts/daily_update.py`. This documents the design, guarantees, and roadmap.

## Purpose

Automatically discover **new candidate reports** from approved humanitarian data services and
drop them into a review queue — **without ever writing to the verified dataset.** It supplies
leads; humans supply verification.

## Sources (scope-locked)

- **HDX (Humanitarian Data Exchange) CKAN API** — no registration; run by OCHA. Primary.
- **ReliefWeb API** — secondary; requires an approved `appname` (see `README_AUTOMATION.md`).
  If not approved, it is skipped cleanly without breaking the run.

Scope is fixed to Phase 1 (Palestine/Gaza) and Phase 2 (Sudan). Adding another country
requires updating project scope first.

## Core guarantee

The script **only** appends to `data/staging/pending_review.csv` with
`verification_status=unverified`, `confidence_level=low`. It never edits `events.csv`,
`persons.csv`, or `famous_victims.csv`. Promotion is a separate, manual, source-checked step
via `scripts/promote_entry.py`.

## Flow

```
daily_update.py ──> data/staging/pending_review.csv   (unverified leads, de-duplicated by staging_id)
        │
        ▼ (human opens URL, verifies against the real source)
promote_entry.py ──> data/phase<N>/events.csv + sources.csv   (verified row, full citation)
        │
        ▼
validate_dataset.py ─> renumber_records.py ─> build_exports.py
```

## De-duplication

Each lead gets a deterministic `staging_id` (phase + system + date + title hash). Existing IDs
are skipped, so re-running daily does not create duplicate leads.

## Scheduling

Windows Task Scheduler (documented in `README_AUTOMATION.md`) or cron:
`conda run -n civid python scripts/daily_update.py`.

## Recommended extensions (roadmap)

1. **Extract citable facts, not just dataset titles.** Current HDX leads are dataset-level
   landing pages (Tier D). Add a per-report text fetch so a reviewer sees a candidate figure.
2. **ACLED API** (registered key) for structured conflict events — never scrape ACLED's site.
3. **`candidate_famous` flag** column to route notable-case leads into the famous-victims
   review pipeline (see `docs/famous_victims_policy.md`).
4. **rejected.csv integration** so dismissed leads are logged with a reason, not just deleted.
5. **Auto-run `validate_dataset.py`** after any promotion and refuse to leave the tree dirty.

## Guardrails

- No blogs, no social media, no uncited scraping.
- Leads are never auto-promoted; unverified stays unverified until a human confirms it.
- The verified dataset is only ever changed by a human-run promotion step.
