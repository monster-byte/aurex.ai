"""
AUREX AI - Track Record Logger
يسجل قراراً جديداً بالسجل الدائم فقط لما يتغيّر القرار الفعلي
(مو كل 15 دقيقة، عشان نتجنب تكرار نفس القرار آلاف المرات)
"""

import json
import os
from datetime import datetime, timezone

from .config import LOG_PATH


def load_log() -> list:
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(log: list) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def log_decision_if_changed(signal_result: dict, entry_price: float) -> bool:
    """
    يضيف سجل جديد فقط إذا تغيّر القرار (ai_status أو directional_bias) عن آخر سجل.
    يرجع True إذا أضاف سجل جديد فعلاً.
    """
    decision = signal_result.get("final_decision", {})
    ai_status = decision.get("ai_status")
    directional_bias = decision.get("directional_bias")

    if not ai_status or entry_price <= 0:
        return False

    log = load_log()

    if log:
        last = log[-1]
        if last.get("ai_status") == ai_status and last.get("directional_bias") == directional_bias:
            return False

    new_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ai_status": ai_status,
        "directional_bias": directional_bias,
        "confirmation_score": signal_result.get("confirmation_score"),
        "trade_probability": signal_result.get("trade_probability"),
        "entry_price": round(entry_price, 2),
        "verified": False,
        "outcome": None,
        "price_after": None,
        "price_change_pct": None,
        "verified_at": None,
    }

    log.append(new_entry)
    save_log(log)
    return True
