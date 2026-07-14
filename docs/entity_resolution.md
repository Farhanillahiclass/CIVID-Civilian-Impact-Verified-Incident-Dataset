# CIVID — Entity Resolution

Entity resolution links repeated mentions of the same organization, conflict actor, facility,
or (only when named by a source) person to a single canonical `entity_id`.

## Canonical entities

Canonical entities live in each phase's `entities.csv`. Each has a stable `entity_id`
(`ENT-P<phase>-NN`), a canonical `entity_name`, and an `aka` field for known aliases.

## Resolution rules

1. **Normalize the mention:** lowercase, strip punctuation and legal suffixes, expand or
   record acronyms (e.g. "ICRC" ↔ "International Committee of the Red Cross").
2. **Match against `aka` + `entity_name`.** A mention resolves to an existing entity if it
   matches the canonical name or any listed alias.
3. **New entity:** if no match, create a new row with a new `entity_id`, list observed aliases
   in `aka`, and cite the `source_id` where it first appears.
4. **Actors vs organizations:** conflict actors (`entity_type=conflict_actor`) are recorded
   factually as named by the source. CIVID makes no legal/culpability determination.
5. **Facilities:** hospitals, schools, and infrastructure named repeatedly (e.g. "Al Obeid
   Teaching Hospital") get their own facility entity for linkage.
6. **Persons/leaders:** created **only** when a source explicitly names the individual. Names
   are never inferred or fabricated. Sensitive-victim identities follow the privacy rules.

## Linking

- Events and persons reference entities implicitly through `organization_affiliation` and
  through the `related_event_id` / `source_id` fields on the entity row.
- When the same real actor appears under variant spellings across phases, keep separate
  per-phase `entity_id`s but use identical canonical `entity_name` + `aka` so a cross-phase
  join on name still works.

## Ambiguity

If two candidate entities cannot be confidently distinguished (e.g. two similarly named local
groups), do not merge. Keep both, set `confidence_level=low`, and describe the ambiguity in
`notes`.
