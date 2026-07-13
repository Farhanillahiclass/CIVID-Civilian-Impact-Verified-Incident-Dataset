import csv
from pathlib import Path
for rel in [
    'data/phase1_palestine/events.csv',
    'data/phase2_sudan/events.csv',
    'data/phase1_palestine/persons.csv',
    'data/phase2_sudan/persons.csv',
]:
    path = Path(rel)
    print('FILE', rel)
    with path.open(encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i <= 15:
                print(i, line.rstrip())
    print()
