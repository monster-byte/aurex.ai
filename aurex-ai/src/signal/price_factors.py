"""
AUREX AI - Price-Based Factors
يحسب: Mega-Cap Alignment, Market Regime (SMA50/SMA200), VXN, US10Y, DXY
كل عامل بيرجع score من 0 إلى 100 + status (green/yellow/red)
"""

import yfinance as yf
import pandas as pd

from .config import MEGA_CAPS, REGIME_SYMBOL


def _status_from_score(score: float) -> str:
    if score >= 65:
        return "green"
    if score >= 40:
        return "yellow"
    return "red"


def compute_mega_cap_alignment(price_snapshot: dict) -> dict:
    """
    نسبة الأسهم الصاعدة من أصل 4 (AAPL, MSFT, NVDA, AMZN)
    مثال: 3 صاعدة من 4 = 75%
    """
    up_count = 0
    details = {}
    for symbol in MEGA_CAPS:
        data = price_snapshot.get(symbol)
        if not data:
            continue
        is_up = data["change_pct"] > 0
        details[symbol] = {"change_pct": data["change_pct"], "up": is_up}
        if is_up:
            up_count += 1

    total = len(details) if details else len(MEGA_CAPS)
    score = round((up_count / total) * 100, 2) if total else 0.0

    return {
        "factor": "mega_cap_alignment",
        "score": score,
        "status": _status_from_score(score),
        "details": details,
    }


def compute_market_regime() -> dict:
    """
    Market Regime عبر SMA50 و SMA200 على المؤشر (^NDX):
    - السعر > SMA50 > SMA200  → Bullish قوي (score عالي)
    - السعر < SMA50 < SMA200  → Bearish قوي (score واطي)
    - أي حالة متعارضة (Golden/Death Cross في طور التشكل) → درجات وسطى
    """
    hist = yf.Ticker(REGIME_SYMBOL).history(period="300d", interval="1d")
    if hist.empty or len(hist) < 200:
        return {"factor": "market_regime", "score": 50.0, "status": "yellow",
                "details": {"error": "insufficient_history"}}

    close = hist["Close"]
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1]
    last_price = close.iloc[-1]

    if last_price > sma50 > sma200:
        regime = "BULLISH"
        # كل ما كانت المسافة النسبية بين السعر و SMA50 أكبر، الثقة أعلى (مع سقف)
        strength = min(((last_price - sma50) / sma50) * 100, 10)
        score = 70 + strength * 3  # يتراوح تقريباً 70-100
    elif last_price < sma50 < sma200:
        regime = "BEARISH"
        strength = min(((sma50 - last_price) / sma50) * 100, 10)
        score = 30 - strength * 3  # يتراوح تقريباً 0-30
    else:
        regime = "NEUTRAL / TRANSITIONAL"
        score = 50.0

    score = max(0.0, min(100.0, round(score, 2)))

    return {
        "factor": "market_regime",
        "score": score,
        "status": _status_from_score(score),
        "details": {
            "regime": regime,
            "last_price": round(float(last_price), 2),
            "sma50": round(float(sma50), 2),
            "sma200": round(float(sma200), 2),
        },
    }


def _percentile_rank(series: pd.Series, value: float) -> float:
    """نسبة عدد القيم الأقل من value ضمن السلسلة (0-100)."""
    return float((series < value).sum() / len(series) * 100)


def compute_vxn_factor(price_snapshot: dict) -> dict:
    """
    VXN (تقلب ناسداك): كل ما كان أقل نسبةً لآخر 20 يوم، كل ما كان الوضع "هادئ"
    وداعم لاستمرار الاتجاه → score أعلى.
    """
    hist = yf.Ticker("^VXN").history(period="40d", interval="1d")
    vxn_data = price_snapshot.get("VXN")
    if hist.empty or not vxn_data:
        return {"factor": "vxn", "score": 50.0, "status": "yellow", "details": {"error": "no_data"}}

    current = vxn_data["last_price"]
    recent = hist["Close"].tail(20)
    percentile = _percentile_rank(recent, current)  # كل ما كان أقل من التاريخ → percentile واطي
    score = round(100 - percentile, 2)  # نعكسها: تقلب منخفض = score عالي

    return {
        "factor": "vxn",
        "score": score,
        "status": _status_from_score(score),
        "details": {"current_vxn": current, "percentile_vs_20d": round(percentile, 2)},
    }def _trend_score(pct_change: float, bullish_if_negative: bool, sensitivity: float = 8.0) -> float:
    """
    يحول نسبة تغيّر (%) لسكور 0-100 حول محور 50.
    bullish_if_negative=True يعني: انخفاض القيمة = إيجابي للسوق (متل DXY وUS10Y).
    """
    effective = -pct_change if bullish_if_negative else pct_change
    score = 50 + effective * sensitivity
    return max(0.0, min(100.0, round(score, 2)))


def compute_us10y_factor() -> dict:
    """
    عائد 10 سنوات: انخفاض العائد عادة داعم لأسهم التكنولوجيا (تكلفة تمويل أقل).
    نقيس % التغير خلال آخر 5 أيام تداول.
    """
    hist = yf.Ticker("^TNX").history(period="10d", interval="1d")
    if hist.empty or len(hist) < 6:
        return {"factor": "us10y", "score": 50.0, "status": "yellow", "details": {"error": "no_data"}}

    close = hist["Close"]
    pct_change_5d = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
    score = _trend_score(pct_change_5d, bullish_if_negative=True)

    return {
        "factor": "us10y",
        "score": score,
        "status": _status_from_score(score),
        "details": {"current_yield_pct": round(float(close.iloc[-1]) / 10, 3), "change_5d_pct": round(pct_change_5d, 3)},
    }


def compute_dxy_factor() -> dict:
    """
    مؤشر الدولار: دولار أضعف عادة داعم للأسهم (خصوصاً الشركات متعددة الجنسيات).
    نقيس % التغير خلال آخر 5 أيام تداول.
    """
    hist = yf.Ticker("DX-Y.NYB").history(period="10d", interval="1d")
    if hist.empty or len(hist) < 6:
        return {"factor": "dxy", "score": 50.0, "status": "yellow", "details": {"error": "no_data"}}

    close = hist["Close"]
    pct_change_5d = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
    score = _trend_score(pct_change_5d, bullish_if_negative=True)

    return {
        "factor": "dxy",
        "score": score,
        "status": _status_from_score(score),
        "details": {"current_dxy": round(float(close.iloc[-1]), 2), "change_5d_pct": round(pct_change_5d, 3)},
    }
