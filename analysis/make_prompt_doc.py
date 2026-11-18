r"""Rebuilds docs\prompt_v3_FINAL.txt cleanly from the real prompt in
analysis\llm_classify_v3_FINAL.py.
Run from the project folder:  python analysis\make_prompt_doc.py
"""
import os
import re
from datetime import date

SRC = os.path.join('analysis', 'llm_classify_v3_FINAL.py')
DST = os.path.join('docs', 'prompt_v3_FINAL.txt')

if not os.path.exists(SRC):
    raise SystemExit('Cannot find ' + SRC + ' - run this from the main project folder.')

code = open(SRC, encoding='utf-8').read()

m = re.search(r"^SYSTEM\s*=\s*'''.*?'''", code, flags=re.S | re.M)
if not m:
    raise SystemExit("Could not find a SYSTEM = '''...''' block in " + SRC)
block = m.group(0)

mm = re.search(r"^MODEL\s*=\s*['\"]([^'\"]+)['\"]", code, flags=re.M)
model = mm.group(1) if mm else '(not found in script)'

lines = [
    'Model: ' + model,
    'Script: llm_classify_v3_FINAL.py',
    'Date saved: ' + date.today().strftime('%d-%m-%Y'),
    'Note: Rule 4 was edited. This file is the FINAL v3 prompt, used for the test run and the rerun. '
    'The first gold run (pred_llm_v3.csv, 82.7%) probably used the older version.',
    '-----',
    block,
]
os.makedirs('docs', exist_ok=True)
with open(DST, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')

out = open(DST, encoding='utf-8').read().split('\n')
print('Saved', DST, 'with', len(out) - 1, 'lines')
print('Line 5 :', out[4])
print('Line 6 :', out[5][:60])
print('Last   :', out[-2][-40:])
