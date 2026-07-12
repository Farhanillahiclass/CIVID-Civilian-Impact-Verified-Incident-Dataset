# Phase 1 — Palestine / Gaza

## 1. Source list

- UN OCHA OPT: https://www.ochaopt.org/
- UNRWA: https://www.unrwa.org/
- OHCHR: https://www.ohchr.org/en/countries/occupied-palestinian-territory
- ACLED: https://acleddata.com/

## 2. Data schema confirmation

Use the schema in schema/civid_schema.json for event, person, and source records.

## 3. Citation / provenance plan

- Preserve source_url and citation_text for every record.
- Record supporting sources in the relevant row notes.
- Flag unverified or disputed facts with verification_status and confidence_level.

## 4. First extraction plan

1. Extract high-level humanitarian updates from UN OCHA OPT.
2. Cross-check incident summaries with UNRWA and OHCHR where available.
3. Add corroborating conflict-event references from ACLED.
4. Create initial rows in data/phase1_palestine/events.csv, persons.csv, and sources.csv only when the source explicitly supports the claim.
