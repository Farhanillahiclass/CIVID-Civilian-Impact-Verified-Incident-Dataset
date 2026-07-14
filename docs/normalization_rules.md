# CIVID — Normalization Rules

Normalization keeps fields consistent and machine-usable without ever changing the meaning
of what a source stated.

## General

- **Encoding:** UTF-8. **Line endings:** the repo tolerates CRLF/LF (Git normalizes).
- **Whitespace:** trim leading/trailing spaces in every field. (Fixed real cases:
  `" estimated"` → `"estimated"` in Phase 2.)
- **Quoting:** any field containing a comma, quote, or newline MUST be double-quoted in CSV.
  (Fixed real case: `El Geneina, West Darfur` was unquoted and shifted columns — now quoted.)
- **Empty vs zero:** blank = unknown/not reported. `0` = explicitly reported as zero.
  Never convert blank to 0.

## Field-level

| Field | Rule |
|---|---|
| `phase` | Prefer the numeric form (`1`,`2`,`3`,`4`) per the data dictionary. Legacy values like `phase1_palestine` are tolerated by tooling but should be migrated. |
| `event_date` | ISO `YYYY-MM-DD`. Date ranges: store the end/report date and describe the range in `notes`. |
| `location_type` | Map to a canonical value in `data/reference/location_types.csv` (e.g. `school area`→`school`, `market area`→`market`, `Gaza-wide`→`territory`). |
| `victim_role` | Controlled vocabulary only (`data/reference/roles.csv`). |
| `victim_age_group` | `child` (<18), `adult` (18+), or `unknown`. Derived from `victim_age` only when age is present. |
| `verification_status` | Lowercase enum: `verified`,`estimated`,`unverified`,`disputed`. |
| `confidence_level` | Lowercase enum: `high`,`medium`,`low`. |
| booleans | Lowercase `true`/`false`. |
| `reliability_score` | Float 0.0–1.0, tiered per `data/reference/source_reliability_tiers.csv`. |
| `source_url` | Store canonical URL; strip tracking query params where safe. Used as dedup key. |

## What normalization must NOT do

- Do not "fill in" missing values.
- Do not infer age, gender, role, or affiliation.
- Do not round, re-estimate, or combine source figures.
- Do not rewrite `citation_text` beyond whitespace trimming.
