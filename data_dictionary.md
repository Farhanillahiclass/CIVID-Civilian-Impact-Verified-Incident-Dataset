# CIVID Data Dictionary

Full column reference for `events.csv`, `persons.csv`, and `sources.csv` across both phases.
Source of truth: `.github/copilot-instructions.md` and `schema/civid_schema.json`.

## events.csv

| Column | Description | Allowed values / format |
|---|---|---|
| `record_id` | Unique row identifier | string |
| `phase` | Project phase number | `1`, `2`, `3`, `4` |
| `country` | Country of the event | string |
| `conflict_name` | Named conflict this event belongs to | string |
| `event_id` | Unique event identifier (e.g. `EVT-001`) | string |
| `event_date` | Date the event occurred | `YYYY-MM-DD` |
| `location` | Specific place name | string |
| `location_type` | Type of location | e.g. `city`, `camp`, `hospital`, `corridor` |
| `source_id` | Foreign key to `sources.csv` | string |
| `fatalities` | Number of deaths reported | integer, blank if unknown |
| `injuries` | Number of injuries reported | integer, blank if unknown |
| `missing` | Number reported missing | integer, blank if unknown |
| `verification_status` | How well-supported this record is | `verified`, `estimated`, `unverified`, `disputed` |
| `confidence_level` | Overall confidence in the record | `high`, `medium`, `low` |
| `notes` | Free-text context, disagreements between sources, caveats | string |

## persons.csv

| Column | Description | Allowed values / format |
|---|---|---|
| `record_id` | Unique row identifier | string |
| `event_id` | Foreign key to `events.csv` | string |
| `victim_name` | Name if disclosed by source | string or blank |
| `victim_alias` | Alternate name/spelling if given | string or blank |
| `victim_age` | Exact age if stated by source | integer or blank |
| `victim_age_group` | Age bracket if exact age unknown | string or blank |
| `victim_gender` | Gender if stated by source | string or blank |
| `victim_role` | Controlled role classification | `child`, `adult civilian`, `doctor`, `nurse`, `medic / paramedic`, `teacher`, `journalist`, `student`, `aid worker`, `political leader`, `military commander`, `local commander`, `fighter / combatant`, `unknown` |
| `occupation` | Stated occupation, if any | string or blank |
| `doctor_flag` … `commander_flag` | Boolean role flags | `true` / `false` |
| `organization_affiliation` | Named organization, if stated | string or blank |
| `image_available` | Whether a licensed image exists for this record | `true` / `false` |
| `image_url` | URL of the licensed image | string or blank |
| `image_source` | Where the image came from | string or blank |
| `image_license` | License terms for the image | string or blank |
| `image_caption` | Caption as provided by the source | string or blank |
| `media_warning` | Content warning if applicable | string or blank |
| `verification_status` | Same scale as events.csv | see above |
| `notes` | Free-text context | string |

## sources.csv

| Column | Description | Format |
|---|---|---|
| `source_id` | Unique identifier, referenced by events/persons | string |
| `source_name` | Publishing organization | e.g. `OCHA`, `ICRC`, `ACLED` |
| `source_url` | Direct link to the report | URL |
| `source_type` | Type of source | e.g. `situation report`, `press release`, `dataset` |
| `source_date` | Date the source was published | `YYYY-MM-DD` |
| `citation_text` | Exact citation text used for this source | string |
| `reliability_score` | 0.0–1.0 reliability rating assigned during review | float |

## Batch notes

Special rows or notes fields (e.g. `batch_note_icrc_acled`) record known limitations of a
particular data-collection batch, such as source concentration or blocked access to a
preferred source. These are kept visible in the data rather than removed, per the project's
traceability-over-completeness rule.

## Verification status definitions

- **verified** — directly and clearly stated by the cited source.
- **estimated** — the source provides a figure explicitly labeled as an estimate/approximation.
- **unverified** — plausible but not directly confirmed by an authoritative source at time of entry.
- **disputed** — multiple sources disagree; disagreement is detailed in `notes`.
