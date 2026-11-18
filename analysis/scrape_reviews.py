from google_play_scraper import reviews, Sort
import pandas as pd

frames = []
for star in [1, 2, 3, 4, 5]:
    result, _ = reviews('in.swiggy.android', lang='en', country='in',
                        sort=Sort.NEWEST, count=2500, filter_score_with=star)
    frames.append(pd.DataFrame(result))
    print(star, 'stars collected:', len(result))

df = pd.concat(frames)[['reviewId', 'score', 'content', 'at', 'reviewCreatedVersion']]
df.columns = ['review_id', 'rating', 'review_text', 'date', 'app_version']

df = df.dropna(subset=['review_text']).drop_duplicates(subset=['review_text'])
df = df[df['review_text'].str.split().str.len() >= 4]
df.to_csv('data/reviews_swiggy_real.csv', index=False)
print(len(df), 'reviews saved')
print(df['date'].min(), 'to', df['date'].max())
print(df['rating'].value_counts().sort_index())