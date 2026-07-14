# CIVID — Data License & Terms

This file governs the **data** in `data/` and `exports/`. The code, scripts, notebooks,
schema, and repo structure are covered separately by `LICENSE` (MIT).

## Ownership of underlying facts

CIVID does **not** claim ownership of the underlying conflict-impact facts. Each record is
sourced from public humanitarian reporting — including UN OCHA, UNRWA, OHCHR, UNHCR, WHO,
ICRC, ACLED, and others as cited per-row in each phase's `sources.csv`. Those facts remain the
intellectual property of, and governed by the terms of, their original publishers.

## What CIVID adds

CIVID contributes the **organization, structuring, normalization, citation linkage,
verification/confidence labeling, and quality metadata**. This compiled structure and its
metadata are shared for research, analytics, and machine-learning use.

## Your responsibilities when reusing the data

1. **Preserve citations.** Keep the `source_id` → `sources.csv` links so facts remain traceable.
2. **Respect each publisher's terms.** Before redistributing underlying figures, check the
   original source's license/terms (linked per row).
3. **Filter by verification.** Do not present `unverified`, `estimated`, or `low`-confidence
   rows as established fact. Honor `verification_status` and `confidence_level`.
4. **No misleading claims.** Do not aggregate CIVID rows into totals that imply a precision or
   completeness the sources do not support (watch `derived_is_aggregate`).
5. **Privacy & safety.** Follow the rules in `docs/usage_disclaimer.md`: no victim imagery, no
   doxxing, cautious handling of minors and sensitive casualties.

## No warranty

The data is provided "as is", without warranty. Verify against the cited primary source before
any publication or policy use. See `docs/usage_disclaimer.md` for the full disclaimer.
