"""
Voice of the Customer Analysis
--------------------------------
Reads a CSV of app store reviews, buckets them into themes using keyword
matching, counts how often each theme appears, and outputs a bar chart +
a short summary you can drop straight into your README / case study.

Usage:
    python analyze_reviews.py

Edit the THEMES dictionary below to match whatever complaints you see in
your own data before re-running.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "reviews_swiggy.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# ---------------------------------------------------------------------
# 2. Define themes as keyword groups
#    -> Edit these keywords to match the app / complaints you're analyzing
# ---------------------------------------------------------------------
THEMES = {
    "Refund Issues": ["refund", "money back", "deducted", "charged twice", "amount deducted",
                       "cancellation fee", "partial refund", "processing"],
    "Delivery Delay": ["delay", "delayed", "late", "took over", "arriving in", "estimate"],
    "Non-Delivery / Marked Delivered": ["never received", "marked as delivered", "handed over",
                                        "nothing was ever delivered", "missing item"],
    "Poor Customer Support": ["support", "customer care", "chat", "no response", "callback",
                               "hold", "scripted", "escalate"],
    "App Glitches / Payment Errors": ["glitch", "crash", "logged out", "payment failed",
                                       "auto-changed", "auto-cancelled", "system error"],
    "Delivery Partner / Tracking Issues": ["delivery partner", "gps", "tracking", "location",
                                           "unreachable", "couldn't find the address"],
}


def categorize(review_text: str):
    """Return list of themes a review matches (a review can match more than one)."""
    text = review_text.lower()
    matched = [theme for theme, keywords in THEMES.items()
               if any(kw in text for kw in keywords)]
    return matched if matched else ["Uncategorized"]


df["themes"] = df["review_text"].apply(categorize)

# Explode so each theme match gets its own row for counting
exploded = df.explode("themes")
theme_counts = exploded["themes"].value_counts()

print("=" * 50)
print("THEME BREAKDOWN (out of {} reviews)".format(len(df)))
print("=" * 50)
for theme, count in theme_counts.items():
    pct = round(100 * count / len(df), 1)
    print(f"{theme:<25} {count:>3} reviews  ({pct}%)")

# ---------------------------------------------------------------------
# 3. Chart
# ---------------------------------------------------------------------
plt.figure(figsize=(8, 5))
theme_counts.sort_values().plot(kind="barh", color="#E23744")
plt.title("What Users Are Complaining About Most")
plt.xlabel("Number of Reviews Mentioning This Theme")
plt.tight_layout()
chart_path = os.path.join(OUTPUT_DIR, "theme_breakdown.png")
plt.savefig(chart_path, dpi=150)
print(f"\nChart saved to: {chart_path}")

# ---------------------------------------------------------------------
# 4. RICE prioritization for the #1 theme
#    -> Update these estimates based on your own judgement
# ---------------------------------------------------------------------
top_theme = theme_counts.index[0]
RICE = {
    "Reach": 8,       # out of 10 -- how many users affected
    "Impact": 9,       # out of 10 -- how much it hurts them
    "Confidence": 7,   # out of 10 -- how sure we are this is real
    "Effort": 4,       # out of 10 -- lower effort = easier to ship (kept separate)
}
rice_score = round((RICE["Reach"] * RICE["Impact"] * RICE["Confidence"]) / RICE["Effort"], 1)

print("\n" + "=" * 50)
print(f"TOP PROBLEM: {top_theme}")
print("=" * 50)
print(f"RICE inputs: {RICE}")
print(f"RICE Score:  {rice_score}")
