import pandas as pd

# Keyword lists from the guide. Merge in any extra keywords from the
# THEMES dictionary in your existing analyze_reviews.py.
THEMES = {
    'refund': ['refund', 'money back'],
    'support': ['support', 'customer care', 'no response'],
    'delivery_delay': ['late', 'delay', 'took too long'],
    'tracking_partner': ['tracking', 'delivery partner', 'rider'],
    'app_payment': ['crash', 'glitch', 'payment failed', 'bug'],
    'non_delivery': ['never arrived', 'not delivered', 'marked delivered'],
    'wrong_missing_items': ['missing', 'wrong item', 'wrong order'],
    'food_quality': ['cold', 'stale', 'quality', 'taste'],
    'fees_pricing': ['fee', 'charges', 'expensive', 'surge'],
}

# utf-8-sig removes the hidden BOM marker that Excel adds to CSV files
df = pd.read_csv('data/gold_labeled.csv', encoding='utf-8-sig')


def predict(text):
    t = str(text).lower()
    found = [k for k, words in THEMES.items() if any(w in t for w in words)]
    # No match = empty (the keyword method has no "praise only" idea).
    return ','.join(found)


df['pred_themes'] = df['review_text'].apply(predict)
df[['review_id', 'pred_themes']].to_csv('data/pred_keyword.csv', index=False)
print('Saved data/pred_keyword.csv with', len(df), 'rows')
