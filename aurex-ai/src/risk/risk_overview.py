"""
AUREX AI - Risk Overview
يحسب: Daily Risk Budget, VaR (95%), Portfolio Beta, Correlation Risk, Liquidity
بعض الحقول (Current Exposure, Max Drawdown YTD) تحتاج سجل صفقات فعلي
وهي غير متوفرة بعد لحين بناء طبقة تنفيذ/تتبع الصفقات — تظهر كـ "N/A" مؤقتاً.
"""

import yfinance as yf
import numpy as np

from .config import (
    ACCOUNT_EQUITY,
    DAILY_RISK_BUDGET_PCT,
    INDEX_SYMBOL,
    MARKET_SYMBOL,
    LOOKBACK_DAYS,
    VAR_CONFIDENCE,
)


def compute_var_95(returns) -> float:
    if len(returns) < 30:
        return 0.0
    percentile = (1 - VAR_CONFIDENCE) * 100
    var_pct = float(np.percentile(returns, percentile))
    return abs(var_pct)


def compute_beta(asset_returns, market_returns) -> float:
    """asset_returns و market_returns لازم يكونوا pandas Series بنفس نوع الفهرس (تاريخ)."""
    aligned_asset, aligned_market = asset_returns.align(market_returns, join="inner")
    if len(aligned_asset) < 30:
        return 1.0
    covariance = np.cov(aligned_asset.values, aligned_market.values)[0][1]
    market_variance = np.var(aligned_market.values)
    if market_variance == 0:
        return 1.0
    return round(float(covariance / market_variance), 3)

def classify_correlation(avg_corr: float) -> str:
    if avg_corr >= 0.8:
        return "HIGH"
    if avg_corr >= 0.5:
        return "MEDIUM"
    return "LOW"


def compute_risk_overview(mega_cap_symbols: list) -> dict:
    index_hist = yf.Ticker(INDEX_SYMBOL).history(period=LOOKBACK_DAYS, interval="1d")
    market_hist = yf.Ticker(MARKET_SYMBOL).history(period=LOOKBACK_DAYS, interval="1d")

    if index_hist.empty:
        return {"error": "insufficient_index_history"}

    index_returns = index_hist["Close"].pct_change().dropna() * 100
    var_95_pct = compute_var_95(index_returns.values)
    var_95_usd = round(ACCOUNT_EQUITY * (var_95_pct / 100), 2)

   beta = 1.0
    if not market_hist.empty:
        market_returns = market_hist["Close"].pct_change().dropna()
        beta = compute_beta(index_returns, market_returns)
    correlations = []
    for symbol in mega_cap_symbols:
        try:
            hist = yf.Ticker(symbol).history(period=LOOKBACK_DAYS, interval="1d")
            if hist.empty:
                continue
            stock_returns = hist["Close"].pct_change().dropna()
            aligned = index_returns.align(stock_returns, join="inner")
            if len(aligned[0]) < 30:
                continue
            corr = float(np.corrcoef(aligned[0], aligned[1])[0][1])
            correlations.append(corr)
        except Exception:
            continue

    avg_correlation = round(float(np.mean(correlations)), 3) if correlations else None
    correlation_label = classify_correlation(avg_correlation) if avg_correlation is not None else "UNKNOWN"

    daily_risk_budget_usd = round(ACCOUNT_EQUITY * DAILY_RISK_BUDGET_PCT, 2)

    return {
        "account_equity_usd": ACCOUNT_EQUITY,
        "daily_risk_budget_pct": DAILY_RISK_BUDGET_PCT * 100,
        "daily_risk_budget_usd": daily_risk_budget_usd,
        "current_exposure": "N/A — يتطلب سجل صفقات فعلي (غير مُفعّل بعد)",
        "max_drawdown_ytd": "N/A — يتطلب سجل صفقات فعلي (غير مُفعّل بعد)",
        "var_95_pct": round(var_95_pct, 3),
        "var_95_usd": var_95_usd,
        "portfolio_beta": beta,
        "correlation_risk": correlation_label,
        "avg_mega_cap_correlation": avg_correlation,
        "liquidity": "HIGH",
    }
