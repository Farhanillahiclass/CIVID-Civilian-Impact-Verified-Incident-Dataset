# CIVID Data Dictionary

Full column reference for `events.csv`, `persons.csv`, and `sources.csv` across both phases.
Source of truth: `schema/civid_schema.json`, `schema/persons_schema.json`, `schema/sources_schema.json`,
`schema/media_schema.json`, `schema/entities_schema.json`, `schema/roles_schema.json`,
`schema/famous_victims_schema.json`.

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

## entities.csv (entity / leader table)

Organizations, conflict actors, facilities, and — only when a source explicitly names them —
individual leaders. Leader names are never fabricated. Schema: `schema/entities_schema.json`.

| Column | Description | Allowed values / format |
|---|---|---|
| `entity_id` | Unique identifier (`ENT-P<phase>-NN`) | string |
| `phase` | Phase number | `1`–`4` |
| `entity_name` | Canonical name | string |
| `entity_type` | Kind of entity | `organization`, `conflict_actor`, `facility`, `person`, `government_body` |
| `aka` | Known aliases/acronyms (for entity resolution) | string or blank |
| `role_category` | Functional category | string |
| `country` | Country | string |
| `organization_type` | Sub-type | string |
| `related_event_id` | Example linked event | string or blank |
| `source_id` | Source where entity is attested | string |
| `verification_status` | Same scale as events | see above |
| `confidence_level` | Confidence | `high`/`medium`/`low` |
| `notes` | Context, neutrality caveats | string |

## media.csv (media / image index)

Index of licensed, ethically usable media. **No victim/casualty imagery.** No identifiable
images of minors unless already public, relevant, and ethically safe. Schema:
`schema/media_schema.json`.

| Column | Description | Allowed values / format |
|---|---|---|
| `media_id` | Unique identifier | string |
| `phase` | Phase number | `1`–`4` |
| `event_id` / `person_record_id` | Optional links | string or blank |
| `media_type` | Kind of media | `image`, `map`, `chart`, `document`, `other` |
| `image_url` / `image_source` / `image_license` / `image_caption` | Media provenance | string or blank |
| `media_warning` | Content warning | string or blank |
| `subject_type` | What is depicted | `infrastructure`, `aid response`, `map`, `chart`, `location`, `document`, `other` |
| `contains_identifiable_person` | Privacy gate | `true`/`false` |
| `ethics_review_status` | Review gate | `approved`, `rejected`, `pending` |
| `verification_status` | Same scale as events | see above |
| `source_id` | Source | string or blank |
| `notes` | Context | string |

## data/reference/ tables (global controlled vocabularies)

- **`roles.csv`** — role taxonomy: `role_id`, `role_label`, `role_category`, `parent_category`,
  `flag_column`, `default_civilian`, `default_combatant`, `hierarchy_level`, `description`.
  See `docs/role_hierarchy.md`.
- **`location_types.csv`** — `location_type`, `canonical`, `synonyms`, `description`. Used to
  normalize `location_type` (see `docs/normalization_rules.md`).
- **`source_reliability_tiers.csv`** — `tier`, `score_min`, `score_max`, `label`, `examples`,
  `description`. Basis for `reliability_score` (see `docs/source_reliability_scoring.md`).

## exports/ derived fields (generated by scripts/build_exports.py)

These are computed, never hand-entered. Source data is joined and quality flags added.

| Field | Meaning |
|---|---|
| `derived_global_event_key` | `phase_dir/event_id` — globally unique key (event_id is unique per phase) |
| `derived_year` / `derived_month` | parsed from `event_date` |
| `derived_timeline_order` | integer ordering across the whole dataset by date then id |
| `derived_is_aggregate` | true if the row looks like a cumulative/aggregate figure |
| `derived_missing_data_flag` | true if key location/date/source or all count fields are blank |
| `derived_ambiguity_flag` | true if `estimated`/`unverified`/`disputed` or `low` confidence |
| `derived_needs_review` | true if `unverified` or `reliability_score` is blank (drives review queue) |

Note: `event_id` is unique **per phase**; use `derived_global_event_key` (or `phase` + `event_id`)
as the global key when combining phases.

## New person fields (v3)

Appended to every `persons.csv` (and mirrored in `famous_victims.csv`):

| Column | Description | Format |
|---|---|---|
| `is_famous` | Whether this person is tracked in the famous-victims special section | `true`/`false` |
| `fame_reason` | Why the person is notable (only if `is_famous`) | string or blank |
| `summary_brief` | Short neutral, source-based summary | string or blank |
| `death_context` | Neutral, source-stated circumstances | string or blank |
| `verified_by` | Pipe-separated list of corroborating authoritative sources | e.g. `OHCHR\|Reuters` |
| `legacy_record_id` | Original id before sequential renumbering (provenance) | string |

## famous_victims.csv (7th table — special section)

Separate, ethically-gated table for notable/publicly-reported individuals. **Never fabricated;
starts empty and is populated only through the human-reviewed pipeline** in
`docs/famous_victims_policy.md`. Schema: `schema/famous_victims_schema.json`.

| Column | Description |
|---|---|
| `famous_id` | Sequential row id (unique per phase) |
| `legacy_record_id` | Original id before renumbering |
| `phase` / `country` / `conflict_name` | Context |
| `event_id` / `person_record_id` | Optional links to events/persons |
| `victim_name` / `victim_alias` | Identity (only if publicly & authoritatively reported) |
| `victim_age` / `victim_age_group` / `victim_gender` | Demographics if stated |
| `victim_role` | Controlled vocabulary |
| `occupation` / `organization_affiliation` | If stated |
| `is_famous` / `fame_reason` / `summary_brief` / `death_context` | Notability + neutral context |
| `event_date` / `location` | When/where, if stated |
| `image_*` / `media_warning` | Only public, licensed, ethically-safe media |
| `source_id` / `source_url` / `citation_text` | Provenance (required) |
| `verified_by` | Corroborating sources, pipe-separated (required, >=1) |
| `verification_status` / `confidence_level` | Per-row certainty (required) |
| `notes` | Context, caveats |

## Record renumbering (v3)

`scripts/renumber_records.py` re-generates each table's row primary key as a gap-free
sequence `1..N` per table per phase:
- `record_id` (events, persons), `famous_id` (famous_victims) become sequential integers.
- The original id is preserved in `legacy_record_id` (never lost; idempotent on re-run).
- `event_id` is the **stable** cross-table business key and is **never** renumbered.
- `famous_victims.person_record_id` is remapped when persons are renumbered (FK-safe).
- A change log is written to `CHANGELOG_renumber.md`.
