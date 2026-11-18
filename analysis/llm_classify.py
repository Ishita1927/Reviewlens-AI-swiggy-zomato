import os, sys, json, time
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
MODEL = 'gemini-3.5-flash-lite'
SLEEP = 6  # seconds between calls, keeps you under free-tier limits

SYSTEM = '''You label app store reviews for a food delivery app.
Allowed themes (use ONLY these names):
- refund: refund slow, partial, missing or stuck
- support: customer support unhelpful, slow, or bot only
- delivery_delay: order arrived late
- tracking_partner: tracking wrong, or problems with the delivery partner
- app_payment: app crashes, glitches, payment errors
- non_delivery: order never arrived or marked delivered wrongly
- wrong_missing_items: wrong or missing items in the order
- food_quality: food cold, stale or poor quality
- fees_pricing: high fees, surge charges, price complaints
- other: a real complaint that fits none of the above
Rules:
- A review can have several themes. Pick only themes the reviewer actually
complains about.
- If the review is only praise, return an empty list.
Return ONLY a JSON object with keys: themes (list of theme names), sentiment
(positive, neutral or negative), severity (1 = minor annoyance, 2 = serious
problem, 3 = ready to quit the app), quote (a short exact phrase copied from
the review that justifies your labels).'''


def classify(text):
    for attempt in range(4):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents='Review: ' + str(text),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM,
                    response_mime_type='application/json',
                    temperature=0 if attempt == 0 else 0.4))
            raw = resp.text
            raw = raw[raw.find('{'): raw.rfind('}') + 1]
            out = json.loads(raw)
            time.sleep(SLEEP)
            return out
        except Exception as e:
            print('retry', attempt, e)
            time.sleep(10 * (attempt + 1))
    return {'themes': ['error'], 'sentiment': '', 'severity': 0, 'quote': ''}


def main():
    infile, outfile = sys.argv[1], sys.argv[2]
    df = pd.read_csv(infile)

    # Resume support: skip reviews already done if the script was stopped
    rows = []
    done = set()
    if os.path.exists(outfile):
        old = pd.read_csv(outfile)
        rows = old.to_dict('records')
        done = set(old['review_id'])

    for i, r in df.iterrows():
        if r['review_id'] in done:
            continue
        out = classify(r['review_text'])
        rows.append({'review_id': r['review_id'],
                     'pred_themes': ','.join(out.get('themes', [])),
                     'pred_sentiment': out.get('sentiment', ''),
                     'pred_severity': out.get('severity', 0),
                     'quote': out.get('quote', '')})
        if i % 10 == 0:
            print(i, 'done')
            pd.DataFrame(rows).to_csv(outfile, index=False)
    pd.DataFrame(rows).to_csv(outfile, index=False)


if __name__ == '__main__':
    main()