# CIVID Record Renumbering Change Log

Run: 2026-07-18T15:46:06+00:00 

event_id is the stable cross-table key and is never renumbered. Row primary keys are renumbered 1..N per table; the original id is kept in `legacy_record_id`.


## phase1_palestine
- events: 42 row(s) renumbered 1..42
- persons: 7 row(s) renumbered 1..7
- famous_victims: 0 row(s) renumbered 1..0

## phase2_sudan
- events: 16 row(s) renumbered 1..16
- persons: 3 row(s) renumbered 1..3
- famous_victims: 0 row(s) renumbered 1..0

## phase3_iran
- events: 5 row(s) renumbered 1..5
- persons: 4 row(s) renumbered 1..4
- famous_victims: 0 row(s) renumbered 1..0

## phase4_additional
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0
