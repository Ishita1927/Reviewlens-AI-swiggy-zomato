import sys
import os
import matplotlib
matplotlib.use('Agg')  # draw to a file, no pop-up window
import matplotlib.pyplot as plt
import pandas as pd

reviews_file = sys.argv[1] if len(sys.argv) > 1 else 'data/reviews_run_sample.csv'
pred_file = sys.argv[2] if len(sys.argv) > 2 else 'data/pred_llm_full.csv'
os.makedirs('analysis/output', exist_ok=True)
pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 20)

reviews = pd.read_csv(reviews_file, encoding='utf-8-sig')
pred = pd.read_csv(pred_file, encoding='utf-8-sig')
need = {'review_id', 'rating', 'date', 'app_version'}
if not need <= set(reviews.columns) or not {'review_id', 'pred_themes', 'pred_severity'} <= set(pred.columns):
    print('Reviews columns:', list(reviews.columns))
    print('Prediction columns:', list(pred.columns))
    sys.exit('A needed column is missing - send me these two lines.')

reviews['date'] = pd.to_datetime(reviews['date'], errors='coerce')
df = reviews.merge(pred, on='review_id', how='inner')
pred['pred_themes'] = pred['pred_themes'].fillna('')
is_err = df['pred_themes'].fillna('').str.contains('error')
print('Reviews in file:', len(reviews), '| matched with predictions:', len(df),
      '| rows marked error (excluded):', int(is_err.sum()))
df = df[~is_err].copy()
n_reviews = df['review_id'].nunique()
print('Reviews analysed:', n_reviews)
praise = (df['pred_themes'].fillna('') == '').sum()
print('Reviews with no complaint theme (praise):', int(praise))

df['themes'] = df['pred_themes'].fillna('').str.split(',')
df = df.explode('themes')
df['themes'] = df['themes'].fillna('').str.strip()
df = df[df['themes'] != '']
df['pred_severity'] = pd.to_numeric(df['pred_severity'], errors='coerce')

summary = df.groupby('themes').agg(
    mentions=('review_id', 'nunique'),
    avg_rating=('rating', 'mean'),
    avg_severity=('pred_severity', 'mean'),
    severity_points=('pred_severity', 'sum'),
    low_rating_mentions=('rating', lambda s: int((s <= 2).sum())))
summary['pct_of_reviews'] = (summary['mentions'] / n_reviews * 100).round(1)
summary = summary.round(2)
print('\n--- Ranked by mentions ---')
print(summary.sort_values('mentions', ascending=False))
print('\n--- Ranked by severity points (mentions x severity) ---')
print(summary.sort_values('severity_points', ascending=False)[['severity_points', 'avg_severity', 'mentions']])
print('\n--- Ranked by mentions in 1-2 star reviews ---')
print(summary.sort_values('low_rating_mentions', ascending=False)[['low_rating_mentions', 'mentions']])
summary.to_csv('analysis/output/theme_summary.csv')

df['month'] = df['date'].dt.to_period('M').astype(str)
trend = df[df['month'] != 'NaT'].groupby(['month', 'themes']).size().unstack(fill_value=0)
trend.to_csv('analysis/output/trend_table.csv')
trend.plot(figsize=(10, 5), marker='o')
plt.title('Complaint themes by month')
plt.ylabel('Number of reviews mentioning theme')
plt.savefig('analysis/output/trend.png', bbox_inches='tight')
print('\nSaved analysis/output/trend.png, trend_table.csv, theme_summary.csv')

# Share of reviews mentioning each theme, per app version (versions with 30+ reviews)
ver_n = reviews.merge(pred[['review_id']], on='review_id').groupby('app_version').size()
big = ver_n[ver_n >= 30].index
share = (df[df['app_version'].isin(big)].groupby(['app_version', 'themes'])['review_id']
         .nunique().unstack(fill_value=0).div(ver_n[big], axis=0).mul(100).round(1))
share.to_csv('analysis/output/version_theme_share.csv')
print('Saved analysis/output/version_theme_share.csv (versions with 30+ reviews)')
