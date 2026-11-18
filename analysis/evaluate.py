import sys
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report

# utf-8-sig removes the hidden BOM marker that Excel adds to CSV files
gold = pd.read_csv('data/gold_labeled.csv', encoding='utf-8-sig')
pred = pd.read_csv(sys.argv[1], encoding='utf-8-sig')
df = gold.merge(pred[['review_id', 'pred_themes']], on='review_id')


def to_list(s):
    # 'none' (praise only) and empty/NaN all mean "no theme"
    return [t.strip() for t in str(s).split(',')
            if t.strip() and t.strip() not in ('nan', 'none')]


y_true = df['true_themes'].apply(to_list)
y_pred = df['pred_themes'].apply(to_list)

mlb = MultiLabelBinarizer()
mlb.fit(list(y_true) + list(y_pred))
print(classification_report(mlb.transform(y_true), mlb.transform(y_pred),
                            target_names=mlb.classes_, zero_division=0))

same = y_true.apply(sorted) == y_pred.apply(sorted)
print('Rows scored:', len(df))
print('Exact match:', round(same.mean() * 100, 1), '%')
df[~same].to_csv('data/errors.csv', index=False)
