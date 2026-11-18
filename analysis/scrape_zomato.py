from google_play_scraper import reviews, Sort
import pandas as pd
result, _ = reviews('com.application.zomato', lang='en', country='in',
                    sort=Sort.NEWEST, count=3000)
df = pd.DataFrame(result)[['reviewId','score','content','at','reviewCreatedVersion']]
df.columns = ['review_id','rating','review_text','date','app_version']
df = df.dropna(subset=['review_text']).drop_duplicates(subset=['review_text'])
df = df[df['review_text'].str.split().str.len() >= 5]
df.to_csv('data/reviews_zomato_real.csv', index=False)
n = min(300, len(df))
df.sample(n, random_state=42).to_csv('data/reviews_zomato_sample300.csv', index=False)
print(len(df), 'reviews saved | sample of', n, '| dates', df.date.min(), 'to', df.date.max())