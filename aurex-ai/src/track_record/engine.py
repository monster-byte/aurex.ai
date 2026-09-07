"""
AUREX AI - Track Record Engine
يشغّل: تسجيل القرار الجديد (لو تغيّر) + التحقق من القرارات القديمة + حفظ الملخص
"""

import json
import os

from .logger import log_decision_if_changed
from .verifier import verify_pending_entries
from .summary import save_summary


def load_json(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    print("=== AUREX AI | Track Record Engine Run ===")

    signal_result = load_json("data/signal/signal_snapshot.json")
    risk_result = load_json("data/risk/risk_snapshot.json")

    entry_price = 0.0
    position_sizing = risk_result.get("position_sizing", {})
    if position_sizing.get("entry_price"):
        entry_price = position_sizing["entry_price"]

    print("[1/3] فحص إذا القرار تغيّر...")
    added = log_decision_if_changed(signal_result, entry_price)
    print(f"  -> {'تم تسجيل قرار جديد' if added else 'ما في تغيير، ما انسجل شي'}")

    print("[2/3] التحقق من القرارات القديمة (24 ساعة)...")
    verified_count = verify_pending_entries()
    print(f"  -> تم التحقق من {verified_count} قرار")

    print("[3/3] حفظ الملخص...")
    summary = save_summary()
    print(f"  -> إجمالي القرارات المسجلة: {summary['total_signals_logged']}")
    print(f"  -> القرارات المقيّمة: {summary['graded_signals']}")
    print(f"  -> نسبة النجاح: {summary['win_rate_pct']}%")

    print("=== انتهى ✅ ===")


if __name__ == "__main__":
    run()
