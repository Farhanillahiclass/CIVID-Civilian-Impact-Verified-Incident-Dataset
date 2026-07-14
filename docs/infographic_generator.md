# CIVID — Infographic Generator Design

Implemented in `scripts/infographic.py` (matplotlib + seaborn). This documents the design and
the intended extensions so the generator stays consistent with the dataset's ethics.

## Purpose

Produce clean, shareable, **non-graphic** visual summaries directly from the production CSVs —
no manual chart building, fully regenerable, and safe to publish (aggregate figures only, no
victim imagery or identifiable personal data).

## Current output (implemented)

`python scripts/infographic.py` reads each phase's `events.csv`, then renders a 3-panel PNG to
`data/staging/live_dashboard_preview.png`:
1. **Reported human cost** — summed fatalities / injuries / missing per phase.
2. **Verification state** — record counts by `verification_status`.
3. **Source trust** — record counts by `confidence_level`.

## Design principles

- **Source of truth = CSVs.** Never hard-code numbers; always aggregate live.
- **Aggregate only.** Charts show counts/sums, never name or depict individuals.
- **Show uncertainty.** Verification + confidence panels make data quality visible, so a
  reader cannot mistake `unverified` rows for confirmed facts.
- **Deterministic + reproducible.** Re-running reproduces the same image from the same data.

## Recommended extensions (roadmap)

1. **Read from `exports/civid_dashboard.csv`** instead of raw per-phase files, so the
   `derived_*` quality flags (timeline order, aggregate flag, needs-review) are available.
2. **Timeline panel** — events per month using `derived_month` / `derived_timeline_order`.
3. **Reliability-weighted view** — split verified vs estimated vs unverified as stacked bars.
4. **Aggregate-vs-incident split** — use `derived_is_aggregate` so cumulative figures are not
   visually double-counted against single incidents.
5. **Per-phase factsheets** — extend `scripts/detailed_factsheet.py` to emit one PNG per phase.
6. **Caption every figure** with a data-date and a "research/educational, verify at source"
   disclaimer footer.
7. **CI hook** — regenerate on data change and store under `exports/figures/`.

## Guardrails

- Do not chart person-level sensitive attributes.
- Do not imply precision the sources do not support; label estimated/aggregate clearly.
- Keep figures license-clean (matplotlib output is our own; underlying facts stay cited).
