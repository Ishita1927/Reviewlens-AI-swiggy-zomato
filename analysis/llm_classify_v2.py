import os, sys, json, time
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
MODEL = 'gemini-3.5-flash-lite'
SLEEP = 6  # seconds between calls, keeps you under free-tier limits

SYSTEM = '''You label app store reviews for a food delivery and quick-commerce app (Swiggy). Reviews may be in English, Hindi or Hinglish.

Allowed themes (use ONLY these names):
- refund: refund is slow, partial, missing, refused or stuck
- support: customer support or chatbot is unhelpful, slow, rude or unreachable
- delivery_delay: the order arrived late or is taking too long
- tracking_partner: wrong ETA or tracking, or delivery partner behaviour (rude, not calling, ringing the bell repeatedly, slow to be assigned)
- app_payment: the app crashes, freezes or glitches, or a payment fails or is charged wrongly
- non_delivery: the order never arrived, was cancelled by the restaurant or partner, or was marked delivered wrongly
- wrong_missing_items: wrong, missing or different items or quantities
- food_quality: food is cold, stale, spoiled, damaged or tastes bad
   - app_experience: confusing or laggy app, popups, ads, navigation, location problems, missing features or options
- fees_pricing: high fees, hidden charges, surge charges, price complaints
- other: a real complaint that fits none of the above. Never add other when another theme already fits.

Rules:
1. Tag a theme ONLY if the reviewer explicitly complains about it. Do not guess or infer.
2. A review can have several themes, but do not add a theme just because it is related to another one.
3. Confusing or ugly UI, laggy app, pop-up ads, hard navigation, location problems and missing app features are 'app_experience', NOT app_payment and NOT 'other'. Being unable to cancel an order is 'other'.
4. These count as 'other', NOT app_payment: being unable to cancel an order, and defective or poor-quality non-food products (for example Instamart electronics or decorations).
5. Vague complaints with no specific issue ('very poor service', 'bad app') get ['other'].
6. Taking money or 'paise le lete hain' is not a payment error. app_payment needs a failure or a wrong charge.
7. Praise, neutral comments and mentions of coupons or Swiggy Cash that are not complaints get an empty list.
8. If a review is mostly positive or says 'so so' but still complains about something specific, tag that complaint.
9. Do not tag support unless the reviewer talks about customer care, chat support, or a call or email going unanswered.

Return ONLY a JSON object with keys: themes (list of theme names), sentiment (positive, neutral or negative), severity (1 = minor annoyance, 2 = serious problem, 3 = ready to quit the app), quote (a short exact phrase copied from the review that is direct evidence for the themes; if the themes list is empty, use an empty string).'''


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
