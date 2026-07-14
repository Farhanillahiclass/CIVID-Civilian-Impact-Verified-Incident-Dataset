# CIVID — Famous Victims Section: Policy & Scraper Plan

The **famous victims** table (`data/phase<N>_*/famous_victims.csv`, 7th table type) is a
separate special section for notable individuals whose death or disappearance in a covered
conflict has been **publicly and authoritatively reported**. It is the most ethically
sensitive table in CIVID and has the strictest rules.

## Why it starts empty

Per the CIVID core principle, **named-person death data is never fabricated or guessed.** The
table structure, schema, and pipeline exist, but rows are added **only** through the verified,
human-reviewed pipeline below. Empty-by-design is correct, not incomplete.

## Inclusion criteria (all must hold)

1. **Public figure / notable case:** the person is already public (e.g. a known journalist,
   medic, academic, aid worker, official) OR their case has been widely and independently
   reported. Record why in `fame_reason`.
2. **Multiple authoritative citations:** at least two independent approved sources corroborate
   the identity and the death/disappearance. List them pipe-separated in `verified_by`
   (e.g. `OHCHR|Reuters`). A single outlet is not enough.
3. **Ethically safe:** no doxxing, no private/family data, no graphic or unsafe imagery.
   Images only if already public, relevant, licensed, and reusable — otherwise leave blank.
4. **Neutral, factual `death_context`:** describe what sources state; no speculation about
   intent or blame beyond what a source explicitly says.

## Approved sources for this table

OHCHR, UN Commission of Inquiry / Special Rapporteur reports, UN CAAC reports, official
investigative/court documents, and — for corroboration — Reuters, AP, BBC. Advocacy trackers
(e.g. press-freedom or medical bodies) may be used **only** as a lead to find, then confirm
against, the approved sources; they are never the sole basis.

## Scraper / collection pipeline (human-gated)

```
1. LEAD DISCOVERY  (automated, safe)
   - scripts/daily_update.py already pulls report leads from HDX + ReliefWeb into
     data/staging/pending_review.csv (verification_status=unverified).
   - Optionally add named-case leads to the same staging file with a `candidate_famous=true`
     marker column. NEVER scrape social media or blogs.

2. HUMAN VERIFICATION  (manual, required)
   - A reviewer opens each lead, confirms identity + death against >= 2 approved sources.
   - Reject unsafe/unverifiable leads to data/staging/rejected.csv with a reason.

3. STRUCTURED ENTRY  (assisted)
   - Only after verification, add a row to the correct phase's famous_victims.csv with:
     victim_name, victim_role (controlled vocab), fame_reason, summary_brief, death_context,
     source_id(s), source_url, citation_text, verified_by (pipe-separated), verification_status,
     confidence_level. Link person_record_id/event_id if a matching row exists.
   - Media fields stay blank unless an image is public + licensed + ethically safe.

4. VALIDATE + RENUMBER + EXPORT
   - python scripts/validate_dataset.py   (enforces citation_text + verified_by present)
   - python scripts/renumber_records.py   (sequential famous_id, legacy preserved)
   - python scripts/build_exports.py       (adds to exports/civid_famous_victims_all.*)
```

## Validation enforcement

`scripts/validate_dataset.py` rejects any famous-victims row that lacks `citation_text` or
`verified_by`, checks `victim_role` against the controlled vocabulary, and verifies
`person_record_id` / `event_id` / `source_id` foreign keys. This makes it structurally
impossible to commit an uncited famous-victim row.

## What must never happen

- No unverified name, age, role, or death detail.
- No inferred religion, ethnicity, or other sensitive attribute unless a source states it.
- No graphic, private, or minor imagery.
- No presenting a single-source claim as established fact.
