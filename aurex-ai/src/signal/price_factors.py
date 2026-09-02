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
    hist = yf.Ticker(REGIME_SYMBOL).history(period="300d", interval="1d")
    if hist.empty or len(hist) < 200:
        return {"factor": "market_regime", "score": 50.0, "status": "yellow", "details": {"error": "insufficient_history"}}

    close = hist["Close"]
    sma50 = close.rolling(50).mean().iloc[-1]
    sma200 = close.rolling(200).mean().iloc[-1]
    last_price = close.iloc[-1]

    if last_price > sma50 > sma200:
        regime = "BULLISH"
        strength = min(((last_price - sma50) / sma50) * 100, 10)
        score = 70 + strength * 3
    elif last_price < sma50 < sma200:
        regime = "BEARISH"
        strength = min(((sma50 - last_price) / sma50) * 100, 10)
        score = 30 - strength * 3
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
    return float((series < value).sum() / len(series) * 100)


def compute_vxn_factor(price_snapshot: dict) -> dict:
    hist = yf.Ticker("^VXN").history(period="40d", interval="1d")
    vxn_data = price_snapshot.get("VXN")
    if hist.empty or not vxn_data:
        return {"factor": "vxn", "score": 50.0, "status": "yellow", "details": {"error": "no_data"}}

    current = vxn_data["last_price"]
    recent = hist["Close"].tail(20)
    percentile = _percentile_rank(recent, current)
    score = round(100 - percentile, 2)

    return {
        "factor": "vxn",
        "score": score,
        "status": _status_from_score(score),
        "details": {"current_vxn": current, "percentile_vs_20d": round(percentile, 2)},
    }


def _trend_score(pct_change: float, bullish_if_negative: bool, sensitivity: float = 8.0) -> float:
    effective = -pct_change if bullish_if_negative else pct_change
    score = 50 + effective * sensitivity
    return max(0.0, min(100.0, round(score, 2)))


def compute_us10y_factor() -> dict:
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
        "details": {"current_yield_pct": round(float(close.iloc[-1]), 3), "change_5d_pct": round(pct_change_5d, 3)},    } 
def compute_dxy_factor() -> dict:
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
