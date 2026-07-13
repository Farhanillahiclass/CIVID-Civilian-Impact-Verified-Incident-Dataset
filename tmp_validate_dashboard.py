import json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path.cwd()
nb_path = root / 'notebooks' / 'master_dashboard.ipynb'
nb = json.loads(nb_path.read_text(encoding='utf-8'))
ns = {'pd': pd, 'Path': Path, 'plt': plt}
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        src = ''.join(cell.get('source', [])) if isinstance(cell.get('source'), list) else cell.get('source', '')
        exec(src, ns)

print('summary')
print(ns['summary'].to_string(index=False))
print('phase_summary')
print(ns['phase_summary'].to_string(index=False))
print('verification_counts')
print(ns['verification_counts'].to_string(index=False))
