# CIVID — Civilian Impact Verified Incident Dataset

**Author / Maintainer:** Muhammad Farhan
**License:** code MIT (© Muhammad Farhan); underlying data per publisher — see `DATA_LICENSE.md`.

A clean, source-verified, multi-country conflict impact dataset built for research,
analytics, and machine learning use — with strict citation, provenance, and ethics
requirements on every record.

## Purpose

CIVID collects verifiable, citable data on civilian-impacting events in active conflict
zones — casualties, displacement, health-system disruption, infrastructure damage — from
authoritative humanitarian sources only. Every record traces back to a named source with
a URL and citation text. Nothing is invented, estimated silently, or presented as more
certain than the source allows.

## What's included

| Phase | Country | Status | Events | Sources |
|---|---|---|---|---|
| 1 | Palestine / Gaza | Active | 35 (27 verified, 8 unverified/pending review) | 16 (OCHA, UNRWA, OHCHR, ACLED, HDX, SCR) |
| 2 | Sudan | First two batches complete | 12 verified/estimated | ICRC, ACLED (diversification flagged, see notes below) |
| 3 | Iran-related events | Scaffolding only — empty by design | 0 | see `docs/` phase notes |
| 4 | Additional countries | Scaffolding only — empty by design | 0 | see `docs/` phase notes |

> **Combined snapshot (from `exports/summary.json`):** 47 events (34 verified, 8 unverified),
> 9 person records, 0 media, 0 famous-victim rows (the famous-victims special section is
> present but empty by design — populated only via the human-reviewed pipeline in
> `docs/famous_victims_policy.md`). Regenerate with `python scripts/build_exports.py`.

**Phases 3 & 4 are intentionally empty.** Per the core no-fabrication principle, their full
table structure and plan files exist, but **no event/victim data is added until backed by an
authoritative, cited source and human-reviewed.** Nothing is invented to "fill" a phase.

**Phase 1 update (14 July 2026):** 8 verified events (EVT-028..035, from OCHA oPt SitRep
10 July 2026, UNRWA SitRep #229, and a Security Council Report/OCHA briefing) were merged
in from the `phase1_new_*.csv` drafts. Their draft `event_id`s (EVT-014..021) collided with
existing rows and were renumbered to EVT-028..035 to preserve event-ID uniqueness and the
persons→events foreign key; the renumbering is logged in each row's `notes`. The 8
`unverified` HDX-derived rows (EVT-020..027) remain flagged `low` confidence and await
manual source review before promotion.

**Data quality note:** Phase 2's second batch is concentrated in ICRC and ACLED sources
after WHO/UNHCR/OCHA direct-site fetches were blocked. This is logged as a `batch_note`
in `sources.csv` and flagged for future diversification — it is not hidden or smoothed over.

## Folder structure

```
CIVID/
├── data/
│   ├── reference/                    # Controlled vocabularies (global)
│   │   ├── roles.csv                 # Role taxonomy + hierarchy + flag mapping
│   │   ├── location_types.csv        # Canonical location types + synonyms
│   │   └── source_reliability_tiers.csv
│   ├── phase1_palestine/             # events, persons, sources, media, entities, famous_victims
│   ├── phase2_sudan/                 # events, persons, sources, media, entities, famous_victims
│   ├── phase3_iran/                  # scaffolding (headers only, no data yet)
│   ├── phase4_additional/            # scaffolding (headers only, no data yet)
│   └── staging/                      # pending_review.csv + rejected.csv (human-review queue)
├── schema/                          # JSON Schemas: events, persons, sources, media, entities, roles, famous_victims
├── docs/                            # Quality rules & policies (dedup, normalization, reliability, entity resolution, role hierarchy, ambiguity, usage, famous-victims, infographic, daily script)
├── scripts/
│   ├── validate_dataset.py          # Integrity + controlled-vocab checks (stdlib)
│   ├── renumber_records.py          # Sequential record_id/famous_id, legacy preserved (stdlib)
│   ├── build_exports.py             # Builds exports/ with derived dashboard/ML fields (stdlib)
│   └── ... (daily_update, promote, infographic, etc.)
├── exports/                         # Generated, export-ready CSV/JSON (dashboard + ML ready)
├── notebooks/                       # phase1, phase2, master_dashboard
├── LICENSE                          # MIT (code only)
├── DATA_LICENSE.md                  # Data terms & usage disclaimer
├── data_dictionary.md
├── CHANGELOG_renumber.md            # Record of each sequential renumbering run
└── README.md
```

### Dataset tables (per phase, linkable)

| Table | Purpose | Key |
|---|---|---|
| `events.csv` | Event-level incidents/impacts | `event_id` (unique per phase) |
| `persons.csv` | Victim/person records (only when a source supports them) | `record_id` → `event_id` |
| `sources.csv` | Source registry with reliability scores | `source_id` |
| `media.csv` | Licensed media index (no victim imagery; ethics-gated) | `media_id` |
| `entities.csv` | Organizations, conflict actors, facilities, named leaders | `entity_id` |
| `famous_victims.csv` | Special section: notable publicly-reported individuals (ethics-gated, human-reviewed, empty by design) | `famous_id` |
| `data/reference/roles.csv` | Global role taxonomy + hierarchy | `role_id` |

Row primary keys (`record_id`/`famous_id`) are renumbered to a gap-free `1..N` sequence per
table via `scripts/renumber_records.py`; the original id is preserved in `legacy_record_id`,
and `event_id` stays stable as the cross-table link.

## Quality tooling

```bash
python scripts/validate_dataset.py   # integrity, FK, controlled-vocab, dupes -> exit 0 if clean
python scripts/renumber_records.py   # sequential record_id/famous_id (legacy preserved) + change log
python scripts/build_exports.py      # regenerate exports/ (combined CSV/JSON + derived fields)
python scripts/daily_update.py       # pull new report leads into the staging review queue (unverified)
python scripts/infographic.py        # regenerate aggregate, non-graphic summary charts
```

`build_exports.py` adds clearly-prefixed **derived** fields (never hand-entered):
`derived_year`, `derived_month`, `derived_timeline_order`, `derived_is_aggregate`,
`derived_missing_data_flag`, `derived_ambiguity_flag`, `derived_needs_review`,
`derived_global_event_key`. See `docs/ambiguity_and_missing_data.md`.

### Quality policies (`docs/`)

- `deduplication_rules.md` — dedup keys and merge/keep rules
- `normalization_rules.md` — field normalization (what to fix, what never to touch)
- `source_reliability_scoring.md` — reliability tiers A–E
- `entity_resolution.md` — resolving repeated names to canonical entities
- `role_hierarchy.md` — role vocabulary → flags → categories
- `ambiguity_and_missing_data.md` — missing/ambiguity flags + human-review queue
- `usage_disclaimer.md` — safety, privacy, neutrality, and usage terms
- `famous_victims_policy.md` — ethics rules + human-gated scraper pipeline for the famous-victims table
- `infographic_generator.md` — design of the aggregate, non-graphic chart generator
- `daily_extraction_script.md` — design of the source-safe daily lead-discovery pipeline

## How to run

```bash
conda activate civid
jupyter notebook notebooks/master_dashboard.ipynb
```
Then **Run All** to regenerate every chart and summary table from the current CSVs.

If the `civid` kernel isn't listed in Jupyter:
```bash
pip install ipykernel
python -m ipykernel install --user --name=civid --display-name "Python (civid)"
```

## Methodology & ethics summary

Every record requires at least one source citation (`source_url` + `citation_text`).
Facts not directly supported by a source are marked `unverified` rather than assumed.
Age, gender, and role fields are never inferred — only recorded when a source states them
explicitly, and roles use a fixed controlled vocabulary. No victim or casualty imagery is
collected or displayed; only source-provided, licensed images of infrastructure or aid
response are eligible for inclusion, and only when the source's own license permits reuse.
Full rules are defined in `docs/` and `schema/*.json`.

## Licensing

- **Code and repo structure** (scripts, notebooks, schema): MIT License.
- **Underlying data**: sourced from public humanitarian reporting (OCHA, UNRWA, ICRC, ACLED,
  and others as cited per-row in `sources.csv`). This dataset does not claim ownership of
  that data — it re-organizes and cites it. Redistribution of the underlying facts should
  respect the terms of each original publishing organization.
- This dataset makes no claims beyond what its cited sources state. Verification status
  and confidence level are recorded per-row precisely so downstream users can filter by
  certainty rather than treat all rows as equally authoritative.

## Disclaimer

This is a research and educational dataset. It is not a legal record, an official casualty
count, or a substitute for the primary humanitarian reports it cites. Always consult the
original source (linked per row) before using any figure in publication or policy work.
