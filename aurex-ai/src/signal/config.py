"""
AUREX AI - Signal Engine Config
الأوزان مطابقة تماماً للوحة AI Signal & Confirmation بالداشبورد الأصلي
"""

# أوزان عوامل التأكيد (المجموع = 100%)
WEIGHTS = {
    "mega_cap_alignment": 0.30,
    "market_regime": 0.15,
    "vxn": 0.10,
    "us10y": 0.15,
    "dxy": 0.10,
    "macro": 0.10,
    "news_sentiment": 0.10,
}

MEGA_CAPS = ["AAPL", "MSFT", "NVDA", "AMZN"]

# رمز المؤشر المستخدم لحساب SMA50/SMA200 (نظام Market Regime)
REGIME_SYMBOL = "^NDX"

# عتبات القرار النهائي (Final Decision)
DECISION_THRESHOLDS = {
    "approve_min_score": 70,   # AI Status = APPROVED (green light)
    "hold_min_score": 50,      # 50-69 = HOLD/MONITOR
    # أقل من 50 = REJECT
}

# كلمات مفتاحية لتصنيف اتجاه المفاجأة الاقتصادية "الجيدة" (Macro Environment factor)
# مؤشرات "الأقل أفضل" (تضخم، بطالة) مقابل "الأعلى أفضل" (نمو، تصنيع)
GOOD_IF_LOWER = ["cpi", "inflation", "ppi", "jobless claims", "unemployment claims", "unemployment rate"]
GOOD_IF_HIGHER = ["gdp", "retail sales", "ism", "pmi", "nonfarm payrolls", "nfp", "consumer confidence", "durable goods"]

# استعلام الأخبار لعامل News & Sentiment (NewsAPI)
NEWS_QUERY = "Nasdaq OR \"Federal Reserve\" OR \"stock market\" OR inflation"
NEWS_MAX_ARTICLES = 25

OUTPUT_PATH = "data/signal/signal_snapshot.json"
