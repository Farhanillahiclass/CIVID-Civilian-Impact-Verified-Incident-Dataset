# CIVID Record Renumbering Change Log

Run: 2026-07-16T13:27:36+00:00 

event_id is the stable cross-table key and is never renumbered. Row primary keys are renumbered 1..N per table; the original id is kept in `legacy_record_id`.


## phase1_palestine
- events: 35 row(s) renumbered 1..35
- persons: 6 row(s) renumbered 1..6
- famous_victims: 0 row(s) renumbered 1..0

## phase2_sudan
- events: 12 row(s) renumbered 1..12
- persons: 3 row(s) renumbered 1..3
- famous_victims: 0 row(s) renumbered 1..0

## phase3_iran
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0

## phase4_additional
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0
