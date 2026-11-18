import math
import pandas as pd

def to_set(s):
    if pd.isna(s):
        return frozenset()
    return frozenset(t.strip() for t in str(s).split(',') if t.strip() and t.strip() != 'none')

def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d * 100, (c + m) / d * 100)

def score(gold_file, pred_file, label):
    g = pd.read_csv(gold_file, encoding='utf-8-sig')
    p = pd.read_csv(pred_file, encoding='utf-8-sig')
    d = g.merge(p[['review_id', 'pred_themes']], on='review_id')
    d = d[~d['pred_themes'].astype(str).str.contains('error')]
    t = d['true_themes'].apply(to_set)
    q = d['pred_themes'].apply(to_set)
    n = len(d)
    exact = sum(a == b for a, b in zip(t, q))
    tp = sum(len(a & b) for a, b in zip(t, q))
    fp = sum(len(b - a) for a, b in zip(t, q))
    fn = sum(len(a - b) for a, b in zip(t, q))
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    lo, hi = wilson(exact, n)
    print(f'{label:18s} n={n:3d} exact={exact / n * 100:5.1f}% (95% range {lo:.0f}-{hi:.0f}%) '
          f'precision={prec:.2f} recall={rec:.2f} F1={f1:.2f}')

print('GOLD SET (150 reviews, current labels)')
for label, f in [('keyword baseline', 'data/pred_keyword.csv'),
                 ('LLM v1', 'data/pred_llm_v1.csv'),
                 ('LLM v2', 'data/pred_llm_v2.csv'),
                 ('LLM v3 final', 'data/pred_llm_v3_check.csv')]:
    score('data/gold_labeled.csv', f, label)

print()
print('TEST SET (50 reviews, current labels)')
for label, f in [('LLM v2', 'data/pred_llm_v2_test.csv'),
                 ('LLM v3 final', 'data/pred_llm_v3_test.csv')]:
    score('data/test_labeled.csv', f, label)