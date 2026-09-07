"""
AUREX AI - Track Record Summary
يحسب إحصائيات ملخصة (نسبة النجاح، عدد القرارات...) من السجل الكامل
"""

import json
import os
from datetime import datetime, timezone

from .config import SUMMARY_PATH
from .logger import load_log


def compute_summary() -> dict:
    log = load_log()

    graded = [e for e in log if e.get("verified") and e.get("outcome") in ("correct", "incorrect")]
    correct = [e for e in graded if e["outcome"] == "correct"]

    win_rate = round((len(correct) / len(graded)) * 100, 1) if graded else None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_signals_logged": len(log),
        "graded_signals": len(graded),
        "correct_signals": len(correct),
        "win_rate_pct": win_rate,
        "recent_entries": log[-15:][::-1],
    }


def save_summary() -> dict:
    summary = compute_summary()
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary
