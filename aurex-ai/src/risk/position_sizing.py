"""
AUREX AI - Position Sizing
يحسب حجم الصفقة، وقف الخسارة، أهداف الربح، والقيمة الاسمية
بناءً على القرار النهائي القادم من محرك الإشارة (Signal Engine)
"""

from .config import (
    ACCOUNT_EQUITY,
    RISK_PER_TRADE_PCT,
    STOP_LOSS_PCT,
    TP1_RR_MULTIPLE,
    TP2_RR_MULTIPLE,
    MICRO_NQ_MULTIPLIER,
)


def get_entry_price(price_snapshot: dict) -> float:
    futures = price_snapshot.get("NASDAQ_FUTURES")
    if futures:
        return futures["last_price"]
    index = price_snapshot.get("NASDAQ_100_INDEX")
    if index:
        return index["last_price"]
    return 0.0


def compute_position_sizing(price_snapshot: dict, signal_result: dict) -> dict:
    entry_price = get_entry_price(price_snapshot)
    decision = signal_result.get("final_decision", {})
    bias = decision.get("directional_bias", "NEUTRAL")
    trade_probability = signal_result.get("trade_probability", 50.0) / 100

    if entry_price <= 0 or bias not in ("LONG", "SHORT"):
        return {
            "tradeable": False,
            "reason": f"لا توجد صفقة قابلة للتنفيذ حالياً (directional_bias={bias})",
            "entry_price": entry_price,
        }

    stop_distance = entry_price * STOP_LOSS_PCT
    risk_amount_usd = ACCOUNT_EQUITY * RISK_PER_TRADE_PCT
    dollar_risk_per_contract = stop_distance * MICRO_NQ_MULTIPLIER

    if dollar_risk_per_contract <= 0:
        return {"tradeable": False, "reason": "stop_distance غير صالح", "entry_price": entry_price}

    position_size_contracts = round(risk_amount_usd / dollar_risk_per_contract, 2)
    notional_value = round(entry_price * MICRO_NQ_MULTIPLIER * position_size_contracts, 2)
    leverage_impact = round(notional_value / ACCOUNT_EQUITY, 3)

    if bias == "LONG":
        stop_loss_price = entry_price - stop_distance
        tp1_price = entry_price + stop_distance * TP1_RR_MULTIPLE
        tp2_price = entry_price + stop_distance * TP2_RR_MULTIPLE
    else:
        stop_loss_price = entry_price + stop_distance
        tp1_price = entry_price - stop_distance * TP1_RR_MULTIPLE
        tp2_price = entry_price - stop_distance * TP2_RR_MULTIPLE

    expected_value_r = round(trade_probability * TP1_RR_MULTIPLE - (1 - trade_probability) * 1, 3)

    return {
        "tradeable": True,
        "directional_bias": bias,
        "entry_price": round(entry_price, 2),
        "stop_loss_price": round(stop_loss_price, 2),
        "take_profit_1": round(tp1_price, 2),
        "take_profit_2": round(tp2_price, 2),
        "risk_per_trade_usd": round(risk_amount_usd, 2),
        "risk_per_trade_pct": RISK_PER_TRADE_PCT * 100,
        "recommended_size_contracts": position_size_contracts,
        "instrument": "Micro E-mini Nasdaq-100 (MNQ)",
        "notional_value_usd": notional_value,
        "leverage_impact": leverage_impact,
        "risk_reward_tp1": TP1_RR_MULTIPLE,
        "risk_reward_tp2": TP2_RR_MULTIPLE,
        "expected_value_r": expected_value_r,
    }
