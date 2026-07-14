# CIVID — Ambiguity & Missing-Data Flags

CIVID prefers *traceable gaps* over *invented completeness*. Missing and ambiguous data are
flagged, never filled in. These flags are computed by `scripts/build_exports.py` and written
into the export files (they are derived, not hand-entered).

## Derived flags (in exports)

| Flag | Set when | Purpose |
|---|---|---|
| `derived_missing_data_flag` | any of `location`, `location_type`, `source_id`, `event_date` is blank, OR all of `fatalities`/`injuries`/`missing` are blank | surface incomplete rows for review |
| `derived_ambiguity_flag` | `verification_status` in {`estimated`,`unverified`,`disputed`} OR `confidence_level` = `low` | surface uncertain rows for filtering |
| `derived_is_aggregate` | `location`/`notes` contains cumulative/aggregate/reporting-period language | separate aggregate figures from single incidents |
| `derived_needs_review` | `verification_status`=`unverified` OR `reliability_score` is blank | drives the human-review queue |

## Human-review queue

- New candidate reports land in `data/staging/pending_review.csv`
  (`verification_status=unverified`, `confidence_level=low`).
- Rows with `derived_needs_review=true` in exports should be worked down before publication.
- Reviewed-and-rejected candidates go to `data/staging/rejected.csv` with a reason, so the
  decision trail is preserved.

## Missing-fields policy (summary)

- Blank = unknown; never guessed.
- Aggregate-only sources stay aggregate; do not force person-level rows.
- Person-level rows exist only when a source supports individual data.
- If a field cannot be verified, leave it blank and, if relevant, explain in `notes`.
- Traceability beats completeness when the two conflict.
