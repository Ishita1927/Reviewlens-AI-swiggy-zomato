import pandas as pd

df = pd.read_csv('data/reviews_window.csv')
parts = [g.sample(min(30, len(g)), random_state=42) for _, g in df.groupby('rating')]
gold = pd.concat(parts).sample(frac=1, random_state=42)
gold[['review_id', 'rating', 'review_text']].to_csv('data/gold_to_label.csv', index=False)
print(len(gold), 'reviews saved to label')
print(gold['rating'].value_counts().sort_index())