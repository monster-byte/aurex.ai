"""
AUREX AI - Signal Engine Config
الأوزان مطابقة تماماً للوحة AI Signal & Confirmation بالداشبورد الأصلي
"""

# أوزان عوامل التأكيد (المجموع = 100%)
# تمت إعادة توزيع الأوزان القديمة (×0.9) لإفساح 10% لعامل "زخم براءات الاختراع" الجديد
WEIGHTS = {
    "mega_cap_alignment": 0.27,
    "market_regime": 0.135,
    "vxn": 0.09,
    "us10y": 0.135,
    "dxy": 0.09,
    "macro": 0.09,
    "news_sentiment": 0.09,
    "patent_momentum": 0.10,
}

MEGA_CAPS = ["AAPL", "MSFT", "NVDA", "AMZN"]

# رمز المؤشر المستخدم لحساب SMA50/SMA200 (نظام Market Regime)
REGIME_SYMBOL = "^NDX"

# عتبات القرار النهائي (Final Decision) — عتبات متناظرة حول نقطة الحياد 50
DECISION_THRESHOLDS = {
    "approve_min_score": 70,   # score >= 70 (وسياق صاعد) → APPROVED LONG
                                # score <= 100-70=30 (وسياق هابط) → APPROVED SHORT (مرآة تلقائية)
    "hold_min_score": 50,      # محفوظ للتوافق الخلفي فقط، غير مستخدم بمنطق العتبات الجديد
}

# كلمات مفتاحية لتصنيف اتجاه المفاجأة الاقتصادية "الجيدة" (Macro Environment factor)
# مؤشرات "الأقل أفضل" (تضخم، بطالة) مقابل "الأعلى أفضل" (نمو، تصنيع)
GOOD_IF_LOWER = ["cpi", "inflation", "ppi", "jobless claims", "unemployment claims", "unemployment rate"]
GOOD_IF_HIGHER = ["gdp", "retail sales", "ism", "pmi", "nonfarm payrolls", "nfp", "consumer confidence", "durable goods"]

# استعلام الأخبار لعامل News & Sentiment (NewsAPI)
NEWS_QUERY = "Nasdaq OR \"Federal Reserve\" OR \"stock market\" OR inflation"
NEWS_MAX_ARTICLES = 25

OUTPUT_PATH = "data/signal/signal_snapshot.json"
