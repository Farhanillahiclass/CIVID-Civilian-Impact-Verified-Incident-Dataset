# CIVID Record Renumbering Change Log

Run: 2026-07-14T15:16:50+00:00 

event_id is the stable cross-table key and is never renumbered. Row primary keys are renumbered 1..N per table; the original id is kept in `legacy_record_id`.


## phase1_palestine
- events: 35 row(s) renumbered 1..35
    - evt_001 -> 1
    - evt_002 -> 2
    - evt_003 -> 3
    - evt_004 -> 4
    - evt_005 -> 5
    - evt_006 -> 6
    - evt_007 -> 7
    - evt_008 -> 8
    - evt_009 -> 9
    - evt_010 -> 10
    - evt_011 -> 11
    - evt_012 -> 12
    - evt_013 -> 13
    - evt_014 -> 14
    - evt_015 -> 15
    - evt_016 -> 16
    - evt_017 -> 17
    - evt_018 -> 18
    - evt_019 -> 19
    - REC-3bcecc12 -> 20
    - REC-4b770da6 -> 21
    - REC-e15f5395 -> 22
    - REC-ca031ffd -> 23
    - REC-29fdc22d -> 24
    - REC-8ee22be6 -> 25
    - REC-b027f769 -> 26
    - REC-bc4eae77 -> 27
    - REC-P014 -> 28
    - REC-P015 -> 29
    - REC-P016 -> 30
    - REC-P017 -> 31
    - REC-P018 -> 32
    - REC-P019 -> 33
    - REC-P020 -> 34
    - REC-P021 -> 35
- persons: 6 row(s) renumbered 1..6
    - per_001 -> 1
    - per_002 -> 2
    - per_003 -> 3
    - per_004 -> 4
    - per_005 -> 5
    - per_006 -> 6
- famous_victims: 0 row(s) renumbered 1..0

## phase2_sudan
- events: 12 row(s) renumbered 1..12
    - evt_020 -> 1
    - evt_021 -> 2
    - evt_022 -> 3
    - evt_023 -> 4
    - evt_024 -> 5
    - evt_025 -> 6
    - evt_026 -> 7
    - evt_027 -> 8
    - evt_028 -> 9
    - evt_029 -> 10
    - evt_030 -> 11
    - evt_031 -> 12
- persons: 3 row(s) renumbered 1..3
    - per_007 -> 1
    - per_008 -> 2
    - per_009 -> 3
- famous_victims: 0 row(s) renumbered 1..0

## phase3_iran
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0

## phase4_additional
- events: 0 row(s) renumbered 1..0
- persons: 0 row(s) renumbered 1..0
- famous_victims: 0 row(s) renumbered 1..0
