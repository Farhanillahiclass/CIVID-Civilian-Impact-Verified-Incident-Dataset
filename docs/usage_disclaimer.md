# CIVID — Usage Disclaimer & Safety Notes

## Nature of this dataset

CIVID is a **research and educational** dataset. It is not a legal record, not an official
casualty count, and not a substitute for the primary humanitarian reports it cites. Always
consult the original source (linked per row in the relevant `sources.csv`) before using any
figure in publication, policy, or legal work.

## Verification is per-row, not blanket

Each row carries `verification_status` and `confidence_level`. Do not treat all rows as equally
authoritative. Filter by these fields for your use case. `unverified`/`low` rows exist for
review workflow and must not be presented as established fact.

## Attribution & neutrality

- Figures attributed to a third party (e.g. OCHA citing a Ministry of Health) are recorded
  with that reporting chain in `notes`. CIVID does not independently re-verify them.
- Conflict actors are recorded factually as named by cited sources. CIVID makes **no** legal,
  culpability, or intent determination about any party.

## Privacy & media safety

- No victim or casualty imagery is collected or displayed.
- No identifiable images of minors are included unless already public, relevant, and
  ethically safe for research; the `media` table enforces an `ethics_review_status` gate and a
  `contains_identifiable_person` flag.
- No doxxing, private images, or unsafe personal data. Person rows are anonymized unless a
  source has already publicly and appropriately named the individual.

## Licensing (see LICENSE and DATA_LICENSE.md)

- **Code / structure / scripts / schema:** MIT License.
- **Underlying facts:** belong to and remain governed by each original publisher (OCHA, UNRWA,
  OHCHR, ICRC, ACLED, etc.). CIVID re-organizes and cites them; it claims no ownership of the
  underlying humanitarian data. Redistribution should respect each publisher's terms.

## No warranty

The dataset is provided "as is", without warranty of any kind. The maintainers are not liable
for downstream use. Errors should be corrected against the cited primary source.
