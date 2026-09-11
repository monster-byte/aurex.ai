"""
AUREX AI - Track Record Verifier
يتحقق من القرارات يلي مر عليها 24 ساعة: هل السعر تحرك بالاتجاه الصح؟
"""

from datetime import datetime, timezone, timedelta

import numpy as np
import yfinance as yf

from .config import VERIFICATION_HOURS, PRICE_SYMBOL
from .logger import load_log, save_log


def find_price_near(target_time) -> float:
    hist = yf.Ticker(PRICE_SYMBOL).history(period="7d", interval="5m")
    if hist.empty:
        return None

    hist.index = hist.index.tz_convert("UTC") if hist.index.tz is not None else hist.index.tz_localize("UTC")
    diffs = np.abs((hist.index - target_time).total_seconds())
    closest_idx = int(np.argmin(diffs))
    return float(hist["Close"].iloc[closest_idx])


def evaluate_outcome(directional_bias: str, price_change_pct: float) -> str:
    if directional_bias == "LONG":
        return "correct" if price_change_pct > 0 else "incorrect"
    if directional_bias in ("SHORT", "SHORT / AVOID"):
        return "correct" if price_change_pct < 0 else "incorrect"
    return "not_graded"


def verify_pending_entries() -> int:
    log = load_log()
    now = datetime.now(timezone.utc)
    verified_count = 0

    for entry in log:
        if entry.get("verified"):
            continue

        entry_time = datetime.fromisoformat(entry["timestamp"])
        if entry_time.tzinfo is None:
            entry_time = entry_time.replace(tzinfo=timezone.utc)

        elapsed_hours = (now - entry_time).total_seconds() / 3600
        if elapsed_hours < VERIFICATION_HOURS:
            continue

        target_time = entry_time + timedelta(hours=VERIFICATION_HOURS)
        price_after = find_price_near(target_time)
        if price_after is None:
            continue

        entry_price = entry["entry_price"]
        price_change_pct = round(((price_after - entry_price) / entry_price) * 100, 3)
        outcome = evaluate_outcome(entry["directional_bias"], price_change_pct)

        entry["verified"] = True
        entry["price_after"] = round(price_after, 2)
        entry["price_change_pct"] = price_change_pct
        entry["outcome"] = outcome
        entry["verified_at"] = now.isoformat()
        verified_count += 1

    if verified_count > 0:
        save_log(log)

    return verified_count
