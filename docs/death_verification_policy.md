# Death Verification Policy — Funeral / Burial / Memorial Confirmation

This rule governs how an **unverified** leader/commander death record is promoted to
**verified** when no equally reliable source contradicts it.

## Trigger condition
A **major reliable outlet** (Reuters, AP, BBC, CNN, Al Jazeera, OHCHR, ACLED, HRANA,
official state media of record, or comparable) reports **funeral, burial, or memorial
rites** for a person described as "late", "slain", "deceased", or equivalent — AND no
equally reliable source contradicts the death.

## Actions taken
When the trigger condition is met:
- `death_status = "dead"`
- `burial_status = "buried"` if burial is explicitly reported; otherwise `"not buried"`.
- `verification_status = "verified"`
- `last_checked = <latest confirmation date>` (ISO `YYYY-MM-DD`)
- `source_set = <all supporting source URLs, pipe-separated>`
- If the record was previously `unverified` / `needs_review = true`, keep a **changelog
  entry** recording the prior state and the promotion.

## Guardrails (no-fabrication)
- This rule is **only** applied when an actual reliable-source report is available and
  inspected. It is NEVER applied on assumption, inference, or social-media rumour.
- If any equally reliable source contradicts the death, the record is set to
  `verification_status = "disputed"` (not "verified").
- `source_set` must contain at least one URL that was actually read/confirmed.
- Records that cannot be verified in the current environment (e.g. network-restricted
  sandbox) stay `unverified` / `needs_review = true` until a cited source is supplied.

## Fields (see `schema/leaders_schema.json`)
`death_status` (enum adds `"dead"`), `burial_status`, `last_checked`, `source_set`.
