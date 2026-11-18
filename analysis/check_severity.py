import pandas as pd

gold = pd.read_csv('data/gold_labeled.csv', encoding='utf-8-sig')
pred = pd.read_csv('data/pred_llm_v3_check.csv', encoding='utf-8-sig')  # use the file that gave 85.3%
df = gold.merge(pred[['review_id', 'pred_severity', 'pred_sentiment']], on='review_id')
df['pred_severity'] = pd.to_numeric(df['pred_severity'], errors='coerce').fillna(0).astype(int)
df['true_severity'] = pd.to_numeric(df['true_severity'], errors='coerce').fillna(0).astype(int)

print('rows compared:', len(df))
print('severity exact match:', round((df['true_severity'] == df['pred_severity']).mean() * 100, 1), '%')
print('severity within 1 point:', round(((df['true_severity'] - df['pred_severity']).abs() <= 1).mean() * 100, 1), '%')
print(pd.crosstab(df['true_severity'], df['pred_severity'], rownames=['you'], colnames=['model']))
print('sentiment exact match:',
      round((df['true_sentiment'].str.lower() == df['pred_sentiment'].str.lower()).mean() * 100, 1), '%')