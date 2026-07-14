# CIVID — Civilian Impact Verified Incident Dataset

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
| 2 | Sudan | First two batches complete | 12 | ICRC, ACLED (diversification flagged, see notes below) |

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
├── .github/copilot-instructions.md   # Full project rules and schema for AI assistants
├── data/
│   ├── phase1_palestine/
│   │   ├── events.csv
│   │   ├── persons.csv
│   │   └── sources.csv
│   └── phase2_sudan/
│       ├── events.csv
│       ├── persons.csv
│       └── sources.csv
├── schema/
│   └── civid_schema.json             # JSON Schema for validation
├── notebooks/
│   ├── phase1_analysis.ipynb
│   ├── phase2_analysis.ipynb
│   └── master_dashboard.ipynb        # Combined view across both phases
├── setup.sh
├── environment.yml
├── data_dictionary.md
└── README.md
```

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
Full rules are defined in `.github/copilot-instructions.md`.

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
