import sys
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report

# Usage: python analysis\evaluate_any.py PRED_FILE GOLD_FILE
pred_file, gold_file = sys.argv[1], sys.argv[2]
gold = pd.read_csv(gold_file)
pred = pd.read_csv(pred_file)
df = gold.merge(pred[['review_id', 'pred_themes']], on='review_id')


def to_list(s):
    items = [t.strip() for t in str(s).split(',')]
    return [t for t in items if t and t not in ('nan', 'none')]


y_true = df['true_themes'].apply(to_list)
y_pred = df['pred_themes'].apply(to_list)
mlb = MultiLabelBinarizer()
mlb.fit(list(y_true) + list(y_pred))
print(classification_report(mlb.transform(y_true), mlb.transform(y_pred),
                            target_names=mlb.classes_, zero_division=0))
same = y_true.apply(sorted) == y_pred.apply(sorted)
print('Rows scored:', len(df))
print('Exact match:', round(same.mean() * 100, 1), '%')
