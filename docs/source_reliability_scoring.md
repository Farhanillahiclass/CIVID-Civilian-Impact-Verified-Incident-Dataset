# CIVID — Source Reliability Scoring

Every source carries a `reliability_score` (0.0–1.0). Scores are tiered, not arbitrary.
Reference table: `data/reference/source_reliability_tiers.csv`.

## Tiers

| Tier | Range | Meaning | Examples |
|---|---|---|---|
| A | 0.95–1.00 | Primary UN humanitarian agency | OCHA, UNRWA, OHCHR, UNHCR, WHO |
| B | 0.90–0.94 | Established humanitarian / conflict monitor | ICRC, ACLED |
| C | 0.80–0.89 | Reputable secondary / corroboration | Security Council Report, Reuters, AP, BBC, HRW, Amnesty |
| D | 0.60–0.79 | Aggregator landing / dataset index | HDX dataset pages, ReliefWeb index |
| E | 0.00–0.59 | Internal note / unscored / low | batch notes, placeholders |
| UNSET | blank | Not yet scored | newly staged sources |

## How a score is assigned

1. Identify the **publishing** organization (not the aggregator). An HDX page that republishes
   an OCHA dataset is Tier D *as a landing page*; extract the underlying OCHA report and cite
   that at Tier A before marking a row `verified`.
2. Place it in the tier above; pick a point value reflecting directness (first-party field
   reporting scores higher within a tier than a summary).
3. Record the score in `sources.csv`.

## Interaction with verification

- A high `reliability_score` does **not** by itself make a row `verified`. Verification
  requires the source to *directly state* the claim.
- A row may be `verified` off a Tier B source, or `unverified` even next to a Tier A source if
  the specific claim isn't directly supported.
- Corroboration by multiple independent sources should be noted and can justify `high`
  `confidence_level`; a single Tier D aggregator alone cannot.

## Aggregate figures attributed to a third party

When a source reports another body's number (e.g. OCHA citing Gaza MoH figures), CIVID records
the reporting chain in `notes` and treats the score of the **citing** source, while making
clear the figure originates with the attributed body. CIVID does not independently re-verify
such figures.
