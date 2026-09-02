"""
AUREX AI - Macro Environment Factor
يحلل أحداث التقويم الاقتصادي عالية الأهمية (من calendar_thisweek.json)
ويقيس هل النتائج الفعلية "مفاجأة إيجابية" أو "سلبية" للسوق
"""

from .config import GOOD_IF_LOWER, GOOD_IF_HIGHER


def _classify_event_direction(title: str):
    title_lower = (title or "").lower()
    for kw in GOOD_IF_LOWER:
        if kw in title_lower:
            return "lower_is_good"
    for kw in GOOD_IF_HIGHER:
        if kw in title_lower:
            return "higher_is_good"
    return None


def _parse_number(value):
    if value is None:
        return None
    try:
        # يشيل % أو K أو أي رموز نصية بسيطة
        cleaned = str(value).replace("%", "").replace("K", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def compute_macro_factor(calendar_payload: dict) -> dict:
    events = calendar_payload.get("high_impact_events", []) if calendar_payload else []

    beats, misses, neutral, evaluated = 0, 0, 0, []

    for ev in events:
        actual = _parse_number(ev.get("actual"))
        forecast = _parse_number(ev.get("forecast"))
        if actual is None or forecast is None:
            continue  # الحدث لسا ما صدر أو ما فيه أرقام قابلة للمقارنة

        direction = _classify_event_direction(ev.get("title", ""))
        if direction is None:
            continue

        if direction == "lower_is_good":
            outcome = "beat" if actual < forecast else ("miss" if actual > forecast else "inline")
        else:
            outcome = "beat" if actual > forecast else ("miss" if actual < forecast else "inline")

        if outcome == "beat":
            beats += 1
        elif outcome == "miss":
            misses += 1
        else:
            neutral += 1

        evaluated.append({"title": ev.get("title"), "actual": actual, "forecast": forecast, "outcome": outcome})

    total = beats + misses + neutral
    if total == 0:
        score = 50.0  # ما في بيانات كافية بعد، نبقى محايدين
    else:
        score = 50 + ((beats - misses) / total) * 50
        score = max(0.0, min(100.0, round(score, 2)))

    status = "green" if score >= 65 else ("yellow" if score >= 40 else "red")

    return {
        "factor": "macro",
        "score": round(score, 2),
        "status": status,
        "details": {"beats": beats, "misses": misses, "neutral": neutral, "evaluated_events": evaluated},
    }
