import pandas as pd

d = pd.read_csv('data/pred_llm_v1.csv')
d = d[d['pred_themes'] != 'error']
d.to_csv('data/pred_llm_v1.csv', index=False)
print(len(d), 'rows kept')