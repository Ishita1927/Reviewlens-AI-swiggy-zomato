import glob
import pandas as pd

def to_set(s):
    if pd.isna(s):
        return frozenset()
    return frozenset(t.strip() for t in str(s).split(',') if t.strip() and t.strip() != 'none')

gold = pd.read_csv('data/gold_labeled.csv', encoding='utf-8-sig')
gold['true'] = gold['true_themes'].apply(to_set)
for f in sorted(glob.glob('data/pred_llm_v3*.csv')) + ['data/pred_llm_v2.csv']:
    p = pd.read_csv(f, encoding='utf-8-sig')
    if 'pred_themes' not in p.columns:
        continue
    d = gold.merge(p[['review_id', 'pred_themes']], on='review_id')
    if len(d) == 0:
        print(f, '| no overlap with the gold set')
        continue
    ok = (d['true'] == d['pred_themes'].apply(to_set)).mean() * 100
    print(f, '| rows matched:', len(d), '| exact match:', round(ok, 1), '%')