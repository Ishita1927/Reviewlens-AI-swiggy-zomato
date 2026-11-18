import glob, os, datetime
import pandas as pd

def when(f):
    return datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%d-%m-%Y %H:%M')

def read_text(f):
    raw = open(f, 'rb').read()
    for enc in ('utf-8-sig', 'utf-16', 'cp1252'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')

for f in sorted(glob.glob('data/pred_*.csv')):
    try:
        d = pd.read_csv(f)
        errs = d['pred_themes'].astype(str).str.contains('error').sum() if 'pred_themes' in d.columns else 'n/a'
        print(f, '|', len(d), 'rows |', errs, 'error rows | saved', when(f))
    except Exception as e:
        print(f, '| could not read:', e)

for f in sorted(glob.glob('data/results_*.txt')):
    print('=====', f, '| saved', when(f))
    print(read_text(f))

f = 'analysis/output/theme_summary.csv'
if os.path.exists(f):
    print('=====', f)
    print(read_text(f))