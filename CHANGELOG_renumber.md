# CIVID Record Renumbering Change Log

Run: 2026-07-18T19:32:02+00:00 

event_id is the stable cross-table key and is never renumbered. Row primary keys are renumbered 1..N per table; the original id is kept in `legacy_record_id`.


## phase1_palestine
- events: 34 row(s) renumbered 1..34
- persons: 7 row(s) renumbered 1..7
- famous_victims: 0 row(s) renumbered 1..0

## phase2_sudan
- events: 18 row(s) renumbered 1..18
- persons: 5 row(s) renumbered 1..5
- famous_victims: 2 row(s) renumbered 1..2

## phase3_iran
- events: 5 row(s) renumbered 1..5
- persons: 4 row(s) renumbered 1..4
- famous_victims: 0 row(s) renumbered 1..0

## phase4_additional
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0
