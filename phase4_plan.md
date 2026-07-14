# Phase 4 Plan — Additional countries

**Status:** SCAFFOLDING ONLY — no data collected yet.
**Data files:** `data/phase4_additional/{events,persons,sources,media,entities}.csv` currently
contain **headers only, zero rows, by design.**

## Purpose

Phase 4 is a reserved, ready-to-use container for additional conflict areas that are only
opened **after Phases 1–3 are complete**. It uses the exact same schema, reference tables,
validation, and export tooling as the earlier phases, so a new country can be added without
any structural changes.

## Rules for opening Phase 4

1. Earlier phases (1–3) must be reviewed and considered complete first.
2. Pick **one** country/conflict area at a time — do not mix countries in one phase batch.
3. Write a scope block (event universe, time window, geography, actor set, exclusions) here
   before extracting anything.
4. Only authoritative, citable sources from the approved list. No fabrication, no guessing.
5. Follow the standard 9-step per-phase workflow and required output order.

## How to add a new country later

- Create `data/phase4_<country>/` (or rename this folder) with the six standard tables.
- Register its sources in `sources.csv` with reliability scores per
  `data/reference/source_reliability_tiers.csv`.
- Run `python scripts/validate_dataset.py` then `python scripts/build_exports.py`.

Until a country is formally opened, this phase remains empty on purpose.
