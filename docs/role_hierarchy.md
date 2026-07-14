# CIVID — Role Hierarchy Mapping

Controlled role vocabulary and hierarchy live in `data/reference/roles.csv`
(schema: `schema/roles_schema.json`). This document explains how roles map to flags and
categories.

## Hierarchy

```
protected_person
├── civilian
│   ├── child                 (child_flag)
│   └── adult civilian        (civilian_flag)
├── healthcare_worker
│   ├── doctor                (doctor_flag)
│   ├── nurse                 (nurse_flag)
│   └── medic / paramedic     (medic_flag)
├── education
│   ├── teacher               (teacher_flag)
│   └── student               (student_flag)
├── media
│   └── journalist            (journalist_flag)
└── humanitarian
    └── aid worker            (organization_affiliation + civilian_flag; no dedicated flag)

actor
└── political leader          (leader_flag)      [civilian/combatant context-dependent]

combatant
├── military commander        (commander_flag + leader_flag)
├── local commander           (commander_flag)
└── fighter / combatant       (combatant_flag)

unknown
└── unknown                   (default when role not stated / not verifiable)
```

## Flag rules

- Set the specific flag(s) for the stated role, plus `child_flag`/`adult_flag` from age, plus
  `civilian_flag` or `combatant_flag` from the role's default — unless the source states
  otherwise.
- `political leader` has **no** default civilian/combatant value; leave both flags `false`
  unless the source clarifies status.
- `military`/`local commander` imply `combatant_flag=true`.
- Healthcare, education, media, and humanitarian roles are protected persons and default to
  `civilian_flag=true`.
- If the role is `unknown`, set no role flags; still set `child_flag`/`adult_flag` if age is
  known.

## Non-fabrication

A role is assigned only when the source states it (occupation, description, or explicit
label). Otherwise use `adult civilian`/`child` (if only age is known) or `unknown`. Never
upgrade `unknown` to a specific role by inference.
