"""
review_voice.py
Answers the 5 interview questions using REVIEW DATA (proxy evidence).
This is NOT a replacement for real interviews. Label it "review-based insights".

Run from the project's main folder:
    python analysis\\review_voice.py data\\reviews_sample600.csv data\\pred_llm_sample600_v3.csv
"""
import os
import re
import sys
from collections import Counter

import warnings

import pandas as pd

warnings.filterwarnings("ignore")

reviews_file, pred_file = sys.argv[1], sys.argv[2]
r = pd.read_csv(reviews_file)
p = pd.read_csv(pred_file)
df = r.merge(p, on="review_id")
df = df[df["pred_themes"].fillna("") != "error"].copy()
df["review_text"] = df["review_text"].fillna("").astype(str)
df["themes"] = df["pred_themes"].fillna("")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["sev"] = pd.to_numeric(df["pred_severity"], errors="coerce")
N = len(df)

lines, quotes = [], []


def out(s=""):
    print(s)
    lines.append(s)


def has(series, rx):
    return series.str.contains(rx, case=False, regex=True, na=False)


def short(t, n=25):
    w = " ".join(t.split()).split(" ")
    return " ".join(w[:n]) + (" ..." if len(w) > n else "")


def signals(title, base, patterns, qname):
    out(f"  {title} (base: {len(base)} reviews)")
    if len(base) == 0:
        out("    (no reviews in this group)")
        return
    for label, rx in patterns.items():
        m = has(base["review_text"], rx)
        k = int(m.sum())
        out(f"    - {label}: {k} ({round(100 * k / len(base), 1)}%)")
        for t in base[m]["review_text"].head(2):
            quotes.append({"question": qname, "signal": label, "snippet": short(t)})


out("REVIEW-BASED ANSWERS TO THE INTERVIEW QUESTIONS (proxy evidence, not interviews)")
out(f"Reviews analysed: {N}")
out("Percentages are keyword-based counts, so they are approximate and may miss Hindi/Hinglish.")
out("")

# ---------------- Q1 ----------------
out("Q1. What went wrong with the order?")
ex = df.assign(t=df["themes"].str.split(",")).explode("t")
ex["t"] = ex["t"].fillna("").str.strip()
ex = ex[ex["t"] != ""]
top = ex.groupby("t")["review_id"].nunique().sort_values(ascending=False)
sup_ids = set(df[has(df["themes"], "support")]["review_id"])
for th, k in top.items():
    ids = set(ex[ex["t"] == th]["review_id"])
    both = len(ids & sup_ids)
    extra = "" if th == "support" else f" | also mention support: {both} ({round(100 * both / k)}%)"
    out(f"    - {th}: {k} reviews ({round(100 * k / N, 1)}%){extra}")
out("")

# ---------------- Q2 ----------------
out("Q2. What did they do next?")
signals("Actions reviewers say they took", df, {
    "contacted support / chat / agent": r"customer (care|service|support)|\bsupport\b|helpline|\bchat\b|\bagent\b|executive",
    "raised a complaint / ticket": r"complain|ticket|raised|reported",
    "called by phone": r"\bcall(ed|ing)?\b|phone",
    "cancelled the order": r"cancel",
    "waited / tried many times": r"waited|waiting|again and again|multiple times|many times|several times",
    "mentions Zomato or another app": r"zomato|magicpin|ondc|rapido|another app|other app",
}, "Q2")
out("")

# ---------------- Q3 ----------------
out("Q3. Did they contact support? Bot or human? How many tries?")
sup = df[has(df["themes"], "support")]
signals("Among reviews tagged support", sup, {
    "bot / automated / AI only": r"\bbot\b|chatbot|chat bot|automated|automatic|\bai\b",
    "no reply / no response": r"no (reply|response)|not respond|never (reply|replied|respond)|didn.?t (reply|respond)|ignored",
    "scripted / same reply": r"same (reply|response|answer|message)|copy.?paste|scripted|template|generic",
    "wants a real person": r"real person|no human|human|talk to (someone|a person)|speak to",
    "asked for photo / proof": r"photo|picture|image|proof|screenshot",
    "could not raise it in the app": r"(can.?t|cannot|unable to|not able to)\s+(raise|file|register|complain|contact)|no option",
    "had to try repeatedly": r"again and again|multiple times|many times|several times|every time|repeatedly",
}, "Q3")
out("")

# ---------------- Q4 ----------------
out("Q4. How long until resolved? Refund? How did they know it was coming?")
ref = df[has(df["themes"], "refund")]
signals("Among reviews tagged refund", ref, {
    "refund not received / still waiting": r"(no|not|never|yet to).{0,25}refund|refund.{0,25}(not|never|pending|stuck|yet)|still waiting|waiting for (my )?(refund|money)",
    "no update / unclear status": r"no (update|status|info|information|notification)|don.?t know|dont know|not clear|unclear|status",
    "partial refund or credits instead": r"partial|wallet|credits?|coupon|instead of",
    "money deducted but order failed": r"deduct|debited|charged",
}, "Q4")
durs = Counter()
for t in ref["review_text"]:
    for n, unit in re.findall(r"(\d+)\s*(hour|hr|day|week)", t.lower()):
        durs[f"{n} {unit}(s)"] += 1
if durs:
    out("    Waiting times mentioned: " + ", ".join(f"{k} (x{v})" for k, v in durs.most_common(8)))
else:
    out("    Waiting times mentioned: none found")
both = int(has(ref["themes"], "support").sum())
out(f"    Refund reviews that also mention support: {both} of {len(ref)}")
out("")

# ---------------- Q5 ----------------
out("Q5. How did they feel afterwards? Did they order again?")
out(f"    Average rating, all reviews: {round(df['rating'].mean(), 2)}")
out(f"    Average rating, support reviews: {round(sup['rating'].mean(), 2)}" if len(sup) else "")
if df["sev"].notna().any():
    out(f"    Model-assigned severity 3 (ready to quit), all reviews: {int((df['sev'] == 3).sum())} ({round(100 * (df['sev'] == 3).mean(), 1)}%)")
    if len(sup):
        out(f"    Severity 3 among support reviews: {int((sup['sev'] == 3).sum())} ({round(100 * (sup['sev'] == 3).mean(), 1)}%)")
signals("Behaviour signals", df, {
    "says will uninstall / stop ordering": r"uninstall|delete the app|deleted the app|never (order|use)|stop(ped)? (using|ordering)|no more|won.?t order|will not order|not ordering|quit",
    "mentions switching to a competitor": r"zomato|magicpin|ondc|rapido|switch",
}, "Q5")
praise_with_issue = df[(df["rating"] >= 4) & (df["themes"].str.strip() != "")]
out(f"    4-5 star reviews that still report a problem: {len(praise_with_issue)}")
out("")

os.makedirs("analysis/output", exist_ok=True)
with open("analysis/output/review_voice.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
pd.DataFrame(quotes).to_csv("data/review_voice_quotes.csv", index=False, encoding="utf-8")
out("Saved analysis/output/review_voice.txt (counts only, safe to commit)")
out("Saved data/review_voice_quotes.csv (contains review text: do NOT commit)")