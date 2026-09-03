"""
AUREX AI - Risk Engine (المرحلة 3)
يجمع Position Sizing و Risk Overview ويحفظهم بملف موحّد
"""

import json
import os
from datetime import datetime, timezone

from .config import OUTPUT_PATH
from .position_sizing import compute_position_sizing
from .risk_overview import compute_risk_overview

MEGA_CAPS = ["AAPL", "MSFT", "NVDA", "AMZN"]


def load_json(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    print("=== AUREX AI | Risk Engine Run ===")

    price_snapshot = load_json("data/prices/snapshot_1D.json")
    signal_result = load_json("data/signal/signal_snapshot.json")

    if not price_snapshot:
        print("[WARN] لا يوجد data/prices/snapshot_1D.json — شغّل طبقة البيانات أولاً")
    if not signal_result:
        print("[WARN] لا يوجد data/signal/signal_snapshot.json — شغّل محرك الإشارة أولاً")

    print("[1/2] حساب حجم الصفقة (Position Sizing)...")
    position_sizing = compute_position_sizing(price_snapshot, signal_result)

    print("[2/2] حساب نظرة عامة على المخاطر (Risk Overview)...")
    risk_overview = compute_risk_overview(MEGA_CAPS)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "position_sizing": position_sizing,
        "risk_overview": risk_overview,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nTradeable          : {position_sizing.get('tradeable')}")
    if position_sizing.get("tradeable"):
        print(f"Entry              : {position_sizing['entry_price']}")
        print(f"Stop Loss          : {position_sizing['stop_loss_price']}")
        print(f"Take Profit 1/2    : {position_sizing['take_profit_1']} / {position_sizing['take_profit_2']}")
        print(f"Recommended Size   : {position_sizing['recommended_size_contracts']} contracts")
        print(f"Expected Value     : {position_sizing['expected_value_r']}R")
    print(f"VaR (95%)          : {risk_overview.get('var_95_pct')}% (${risk_overview.get('var_95_usd')})")
    print(f"Portfolio Beta     : {risk_overview.get('portfolio_beta')}")
    print(f"Correlation Risk   : {risk_overview.get('correlation_risk')}")
    print(f"\n[OK] تم حفظ {OUTPUT_PATH}")
    print("=== انتهى ✅ ===")


if __name__ == "__main__":
    run()
