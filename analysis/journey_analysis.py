import pandas as pd

rev = pd.read_csv('data/reviews_window.csv', encoding='utf-8-sig')
pred = pd.read_csv('data/pred_llm_full_v3.csv', encoding='utf-8-sig')
df = rev.merge(pred, on='review_id', how='inner')
df['pred_themes'] = df['pred_themes'].fillna('')
df = df[~df['pred_themes'].str.contains('error')]
df['T'] = df['pred_themes'].apply(lambda s: [t.strip() for t in s.split(',') if t.strip()])
df['pred_severity'] = pd.to_numeric(df['pred_severity'], errors='coerce')
c = df[df['T'].apply(len) > 0].copy()

print('reviews scored:', len(df), '| complaint reviews:', len(c))
sup = c[c['T'].apply(lambda t: 'support' in t)]
ops = {'refund', 'non_delivery', 'wrong_missing_items', 'delivery_delay',
       'food_quality', 'tracking_partner', 'app_payment'}
both = sup[sup['T'].apply(lambda t: len(ops & set(t)) > 0)]
print('reviews mentioning support:', len(sup))
print('...that also report another operational problem:', len(both),
      f'({len(both) / max(len(sup), 1) * 100:.0f}%)')

for th in ['refund', 'non_delivery', 'wrong_missing_items', 'delivery_delay']:
    sub = c[c['T'].apply(lambda t: th in t)]
    w = sub[sub['T'].apply(lambda t: 'support' in t)]
    print(f'{th}: {len(sub)} reviews, {len(w)} also mention support '
          f'({len(w) / max(len(sub), 1) * 100:.0f}%)')

c['has_support'] = c['T'].apply(lambda t: 'support' in t)
print('average severity, support complaint vs not:')
print(c.groupby('has_support')['pred_severity'].mean().round(2))
print('severity-3 reviews:', (c['pred_severity'] == 3).sum(),
      '| of those mentioning support:', ((c['pred_severity'] == 3) & c['has_support']).sum())
c['band'] = c['rating'].apply(lambda r: '1-2 star' if r <= 2 else '3-5 star')
print('complaint reviews by rating band:')
print(c.groupby('band').size())
print('support complaints by rating band:')
print(c[c['has_support']].groupby('band').size())
print('average severity by band:')
print(c.groupby('band')['pred_severity'].mean().round(2))