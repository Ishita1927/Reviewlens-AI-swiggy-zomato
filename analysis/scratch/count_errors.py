import pandas as pd

d = pd.read_csv('data/pred_llm_v3_rerun.csv')
bad = d['pred_themes'].astype(str).str.contains('error')
print('rows in file:', len(d))
print('rows with error:', bad.sum())
print('columns:', d.columns.tolist())