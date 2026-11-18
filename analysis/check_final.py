import glob, re
import pandas as pd

def grab(path):
    s = open(path, encoding='utf-8').read()
    m = re.search(r"SYSTEM\s*=\s*(?:'''|\"\"\")(.*?)(?:'''|\"\"\")", s, re.S)
    return ' '.join(m.group(1).split()) if m else None

a = grab('docs/prompt_v3_FINAL.txt')
b = grab('analysis/llm_classify_v3_FINAL.py')
print('prompt found in txt file:', a is not None, '| in script:', b is not None)
print('IDENTICAL' if a == b else 'DIFFERENT: fix before reporting any numbers')

allowed = {'refund','support','delivery_delay','tracking_partner','app_payment','non_delivery',
           'wrong_missing_items','food_quality','app_experience','fees_pricing','other','none'}

def names(series):
    return {t.strip() for x in series.dropna() for t in str(x).split(',') if t.strip()}

for f in ['data/gold_labeled.csv', 'data/test_labeled.csv'] + sorted(glob.glob('data/pred_llm_*.csv')):
    try:
        d = pd.read_csv(f)
    except FileNotFoundError:
        continue
    col = 'true_themes' if 'true_themes' in d.columns else 'pred_themes'
    extra = names(d[col]) - allowed
    print(f, '| names not in the final prompt:', sorted(extra) if extra else 'none')