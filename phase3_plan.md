# Phase 3 Plan — Iran-related conflict events

**Status:** SCAFFOLDING ONLY — no data collected yet.
**Data files:** `data/phase3_iran/{events,persons,sources,media,entities}.csv` currently contain
**headers only, zero rows, by design.**

## Why this phase is empty on purpose

The CIVID core principle forbids fabricating or guessing conflict data. Per the project brief,
Phase 3 (Iran-related events) may only be populated **"if the scope is clearly defined and
reliable verified sources exist."** The structure below is ready, but no event, victim, or
casualty row will be added until each is backed by an authoritative, citable source and
reviewed by a human. Nothing here is auto-generated.

## 1. Scope definition (must be finalized before any extraction)

Before adding a single row, pin down and record here:
- **Event universe:** which specific incidents/categories are in scope (e.g. strikes,
  detentions, protest-related casualties, cross-border incidents). Vague "Iran conflict" is
  not an acceptable scope.
- **Time window:** explicit start/end dates.
- **Geography:** specific provinces/cities or cross-border theatres.
- **Actor set:** which parties are in scope.
- **Exclusions:** what is deliberately out of scope, and why.

## 2. Candidate authoritative sources (to be confirmed live before use)

Only sources from the approved list qualify. Candidates to evaluate:
- OHCHR / UN Special Rapporteur reports on Iran
- UN Secretary-General / UN Human Rights Council documents
- ACLED (structured event data)
- ICRC where operational reporting exists
- Reuters / AP / BBC **for corroboration only**, never as sole basis
- Court, sanctions, or official investigative documents where relevant

Do **not** use blogs, opinion pieces, copied Wikipedia text, or scraped social media.

## 3. Workflow (identical to Phases 1–2)

1. Finalize scope (Section 1) → 2. Collect + score source candidates → 3. Extract structured
rows only when a source explicitly supports the claim → 4. Normalize/clean → 5. Deduplicate +
assign confidence → 6. Build citation/provenance links → 7. Export CSV/JSON →
8. Update data dictionary → 9. Recommend next phase.

## 4. Hard gate

Do not begin extraction until (a) Phase 1 and Phase 2 are reviewed as complete, and
(b) the scope in Section 1 is written down and approved. Until then this phase stays empty.
