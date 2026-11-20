import os, sys, json, time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from google.genai import types
import llm_classify_v2 as v2   # reuses the same API client, MODEL and v2 prompt

BATCH = 10      # reviews sent per API call
WORKERS = 2     # calls running at the same time (use 4 if your free limit is 30+ requests/minute)
SLEEP = 1       # seconds each worker waits after a call

BATCH_NOTE = '''

IMPORTANT - OUTPUT FORMAT FOR THIS REQUEST (replaces the single-object format above):
You will receive several reviews, each with a number. Label EACH review independently with the rules above.
Return ONLY a JSON list with exactly one object per review, in the same order. Each object has the keys:
id (the review number as an integer), themes, sentiment, severity, quote.'''


def classify_batch(texts):
    prompt = '\n\n'.join('Review ' + str(i + 1) + ': ' + str(t) for i, t in enumerate(texts))
    for attempt in range(4):
        try:
            resp = v2.client.models.generate_content(
                model=v2.MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=v2.SYSTEM + BATCH_NOTE,
                    response_mime_type='application/json',
                    temperature=0 if attempt == 0 else 0.4))
            raw = resp.text
            raw = raw[raw.find('['): raw.rfind(']') + 1]
            by_id = {int(x['id']): x for x in json.loads(raw)}
            if all((i + 1) in by_id for i in range(len(texts))):
                time.sleep(SLEEP)
                return [by_id[i + 1] for i in range(len(texts))]
            print('retry', attempt, 'missing review numbers')
        except Exception as e:
            print('retry', attempt, e)
            time.sleep(10 * (attempt + 1))
    # last resort: label the reviews one by one with the normal v2 function
    print('batch failed, labeling one by one')
    return [v2.classify(t) for t in texts]


def work(chunk):
    ids = list(chunk['review_id'])
    outs = classify_batch(list(chunk['review_text']))
    return ids, outs


def main():
    infile, outfile = sys.argv[1], sys.argv[2]
    df = pd.read_csv(infile)

    rows, done = [], set()
    if os.path.exists(outfile):
        old = pd.read_csv(outfile)
        rows = old.to_dict('records')
        done = set(old['review_id'])

    todo = df[~df['review_id'].isin(done)]
    chunks = [todo.iloc[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    print(len(todo), 'reviews to do in', len(chunks), 'calls')

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for n, (ids, outs) in enumerate(ex.map(work, chunks), start=1):
            for rid, out in zip(ids, outs):
                rows.append({'review_id': rid,
                             'pred_themes': ','.join(out.get('themes', [])),
                             'pred_sentiment': out.get('sentiment', ''),
                             'pred_severity': out.get('severity', 0),
                             'quote': out.get('quote', '')})
            pd.DataFrame(rows).to_csv(outfile, index=False)
            print(n * BATCH, 'done')
    pd.DataFrame(rows).to_csv(outfile, index=False)


if __name__ == '__main__':
    main()