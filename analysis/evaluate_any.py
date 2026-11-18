r"""Score any prediction file against any labeled file.
Usage (from the project folder):
  python analysis\evaluate_any.py data\test_labeled.csv data\pred_llm_v3_test.csv
"""
import sys
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report

if len(sys.argv) < 3:
    sys.exit('Usage: python analysis\\evaluate_any.py <labeled_csv> <prediction_csv>')

gold = pd.read_csv(sys.argv[1], encoding='utf-8-sig')
pred = pd.read_csv(sys.argv[2], encoding='utf-8-sig')
df = gold.merge(pred[['review_id', 'pred_themes']], on='review_id')


def to_list(s):
    return [t.strip() for t in str(s).split(',')
            if t.strip() and t.strip() not in ('nan', 'none')]


y_true = df['true_themes'].apply(to_list)
y_pred = df['pred_themes'].apply(to_list)

mlb = MultiLabelBinarizer()
mlb.fit(list(y_true) + list(y_pred))
print(classification_report(mlb.transform(y_true), mlb.transform(y_pred),
                            target_names=mlb.classes_, zero_division=0))
same = y_true.apply(sorted) == y_pred.apply(sorted)
print('Rows labeled:', len(gold), '| rows scored:', len(df))
print('Exact match:', round(same.mean() * 100, 1), '%')
out = sys.argv[2].replace('.csv', '_errors.csv')
df[~same].to_csv(out, index=False)
print('Mistakes saved to', out)