"""
error_breakdown.py
Sorts the model's wrong rows into types and prepares a file for writing reasons.

Run from the project's main folder:
    python analysis\\error_breakdown.py data\\errors_v3_gold150.csv
"""
import sys
from collections import Counter

import pandas as pd

e = pd.read_csv(sys.argv[1])


def to_set(s):
    return {t.strip() for t in str(s).split(",")
            if t.strip() and t.strip() not in ("nan", "none")}


extra, missed = Counter(), Counter()
kinds, added_col, missed_col = [], [], []
for _, r in e.iterrows():
    t, p = to_set(r["true_themes"]), to_set(r["pred_themes"])
    ex, mi = p - t, t - p
    extra.update(ex)
    missed.update(mi)
    if ex and mi:
        kind = "both"
    elif ex:
        kind = "model added extra theme"
    elif mi:
        kind = "model missed a theme"
    else:
        kind = "same themes (check 'none' labels)"
    kinds.append(kind)
    added_col.append(", ".join(sorted(ex)))
    missed_col.append(", ".join(sorted(mi)))

e["error_type"] = kinds
e["model_added"] = added_col
e["model_missed"] = missed_col
e["reason"] = ""

print("Error rows:", len(e))
print(e["error_type"].value_counts().to_string())
print("\nThemes the model ADDED:", dict(extra.most_common()))
print("Themes the model MISSED:", dict(missed.most_common()))

cols = ["review_text", "true_themes", "pred_themes", "model_added",
        "model_missed", "error_type", "reason"]
e[cols].to_csv("data/errors_v3_to_label.csv", index=False, encoding="utf-8")
print("\nSaved data/errors_v3_to_label.csv. Open it and fill in the reason column.")