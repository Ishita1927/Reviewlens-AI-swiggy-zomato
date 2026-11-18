import pandas as pd

df = pd.read_csv('data/reviews_swiggy_real.csv', parse_dates=['date'])
start = df.groupby('rating')['date'].min().max()
window = df[df['date'] >= start].copy()
window.to_csv('data/reviews_window.csv', index=False)
print('Shared window starts:', start)
print(len(window), 'reviews in the window')
print(window['rating'].value_counts().sort_index())