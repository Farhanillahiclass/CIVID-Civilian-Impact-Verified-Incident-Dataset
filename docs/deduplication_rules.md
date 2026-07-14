# CIVID — Deduplication Rules

Deduplication protects against the same real-world event or person being counted twice,
especially when multiple sources report it or a staged row is promoted more than once.

## Identity keys

| Table | Primary key | Natural key (for dedup) |
|---|---|---|
| events | `event_id` | `country` + `event_date` + normalized `location` + core figures |
| persons | `record_id` | `event_id` + `victim_name`/`victim_role` + `victim_age` |
| sources | `source_id` | normalized `source_url` |
| entities | `entity_id` | normalized `entity_name` + `phase` |
| media | `media_id` | normalized `image_url` |

## Rules

1. **Hard duplicate (drop / merge):** identical natural key AND same reporting source.
   Keep one row; move the other's unique citation into `notes` if it adds provenance.
2. **Cross-source corroboration (keep, link):** same event reported by different sources is
   NOT a duplicate. Keep one event row and record all supporting `source_id`s (add extra
   citations to `notes`); this raises confidence, it does not create a second event.
3. **Aggregate vs incident:** a cumulative/aggregate figure (e.g. "1,109 killed since 2023")
   and a single incident inside that window are different rows. Never merge an aggregate into
   an incident or vice versa. Aggregates are flagged `derived_is_aggregate` in exports.
4. **Promotion guard:** before promoting a staged row, check its `source_url` and natural key
   against existing rows to avoid re-adding an already-present event.
5. **ID collisions:** `event_id`/`source_id`/`record_id` must be globally unique across the
   dataset. If a draft reuses an existing ID, renumber the draft and log the original ID in
   `notes` (see EVT-028..035 in Phase 1 for a worked example).

## Detection

`python scripts/validate_dataset.py` reports duplicate `event_id`, `record_id`, `source_id`,
`entity_id`, and `media_id` values, plus duplicate normalized `source_url`s, so hard
duplicates surface automatically before commit.
