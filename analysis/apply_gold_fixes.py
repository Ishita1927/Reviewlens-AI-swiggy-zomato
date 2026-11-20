import pandas as pd

gold = pd.read_csv('data/gold_labeled.csv')
gold.to_csv('data/gold_labeled_backup.csv', index=False)  # safety copy

fixes = pd.read_csv('data/error_review_v1_updated.csv')
fixes = fixes[fixes['corrected_true_themes'].notna()]

changed = 0
for _, r in fixes.iterrows():
    mask = gold['review_text'] == r['review_text']
    if mask.sum() == 1:
        gold.loc[mask, 'true_themes'] = r['corrected_true_themes']
        changed += 1
    else:
        print('Could not match one row:', str(r['review_text'])[:60])

gold.to_csv('data/gold_labeled.csv', index=False)
print(changed, 'gold labels updated')
