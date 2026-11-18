import pandas as pd

t = pd.read_csv('data/test_labeled.csv', encoding='utf-8-sig')
v2 = pd.read_csv('data/pred_llm_v2_test.csv', encoding='utf-8-sig')[['review_id', 'pred_themes']].rename(columns={'pred_themes': 'v2'})
v3 = pd.read_csv('data/pred_llm_v3_test.csv', encoding='utf-8-sig')[['review_id', 'pred_themes']].rename(columns={'pred_themes': 'v3'})
d = t.merge(v2, on='review_id').merge(v3, on='review_id')
d = d[d['review_text'].str.lower().str.contains('cancel')]
for _, r in d.iterrows():
    print('YOU:', r['true_themes'], '| v2:', r['v2'], '| v3:', r['v3'])
    print('   ', r['review_text'][:110])