import pandas as pd

for name in ['gold_labeled', 'test_labeled']:
    d = pd.read_csv(f'data/{name}.csv', encoding='utf-8-sig')
    t = d['review_text'].str.lower()
    for w in ['decorat', 'electronic', 'defective', 'cancel', 'instamart']:
        print(name, '|', w, '|', int(t.str.contains(w).sum()), 'reviews')