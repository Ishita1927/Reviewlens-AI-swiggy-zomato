import pandas as pd

gold = pd.read_csv('data/gold_labeled.csv')
pred = pd.read_csv('data/pred_llm_v1.csv')
df = gold.merge(pred, on='review_id')


def norm(s):
    items = [t.strip() for t in str(s).split(',')]
    return sorted([t for t in items if t and t not in ('nan', 'none')])


df['match'] = df['true_themes'].apply(norm) == df['pred_themes'].apply(norm)
errs = df[~df['match']][['review_text', 'true_themes', 'pred_themes', 'quote']].copy()
errs['reason'] = ''
errs.to_csv('data/error_review_v1.csv', index=False)
print(len(errs), 'wrong rows saved')
print((df['pred_themes'] == 'error').sum(), 'rows marked error')