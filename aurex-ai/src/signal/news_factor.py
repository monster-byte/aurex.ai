"""
AUREX AI - News & Sentiment Factor
يسحب أخبار حديثة عبر NewsAPI (newsapi.org) ويحلل المشاعر عبر VADER
يحتاج متغير بيئة NEWSAPI_KEY (مفتاح مجاني من newsapi.org)
"""

import os

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .config import NEWS_QUERY, NEWS_MAX_ARTICLES

NEWSAPI_URL = "https://newsapi.org/v2/everything"
_analyzer = SentimentIntensityAnalyzer()


def fetch_headlines(api_key: str, query: str = NEWS_QUERY, max_articles: int = NEWS_MAX_ARTICLES):
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": api_key,
    }
    resp = requests.get(NEWSAPI_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [
        {"title": a.get("title"), "source": (a.get("source") or {}).get("name"), "publishedAt": a.get("publishedAt")}
        for a in data.get("articles", [])
    ]


def compute_news_factor() -> dict:
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        return {
            "factor": "news_sentiment",
            "score": 50.0,
            "status": "yellow",
            "details": {"error": "NEWSAPI_KEY not set — تم استخدام قيمة محايدة افتراضية"},
        }

    try:
        headlines = fetch_headlines(api_key)
    except Exception as e:
        return {
            "factor": "news_sentiment",
            "score": 50.0,
            "status": "yellow",
            "details": {"error": f"news_fetch_failed: {e}"},
        }

    if not headlines:
        return {"factor": "news_sentiment", "score": 50.0, "status": "yellow", "details": {"error": "no_articles"}}

    scored = []
    total_compound = 0.0
    for h in headlines:
        compound = _analyzer.polarity_scores(h["title"] or "")["compound"]
        total_compound += compound
        label = "Positive" if compound > 0.2 else ("Negative" if compound < -0.2 else "Neutral")
        scored.append({**h, "sentiment": label, "compound": round(compound, 3)})

    avg_compound = total_compound / len(headlines)  # من -1 إلى 1
    score = round((avg_compound + 1) / 2 * 100, 2)  # نحوّلها لمقياس 0-100
    status = "green" if score >= 65 else ("yellow" if score >= 40 else "red")

    overall_sentiment = "BULLISH" if score >= 60 else ("BEARISH" if score <= 40 else "NEUTRAL")

    return {
        "factor": "news_sentiment",
        "score": score,
        "status": status,
        "details": {
            "overall_sentiment": overall_sentiment,
            "avg_compound": round(avg_compound, 3),
            "articles_analyzed": len(headlines),
            "top_headlines": scored[:6],
        },
    }
