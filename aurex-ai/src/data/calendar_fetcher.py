"""
AUREX AI - Economic Calendar Fetcher
يسحب التقويم الاقتصادي الأسبوعي من Forex Factory (JSON عام)
ويطابقه مع لوحة "Key Economic Indicators" و "Upcoming High Impact Events"

ملاحظة: هذا مصدر غير رسمي (public feed) وممكن يتغير أو يتوقف بدون سابق إنذار.
إذا صار في مشكلة، البديل الأكثر استقراراً وموثوقية هو FRED API (مجاني برقم اشتراك).
"""

import json
import os
from datetime import datetime, timezone

import requests

from .config import FF_CALENDAR_URL_THIS_WEEK, OUTPUT_DIR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AUREX-AI-DataBot/1.0)"
}


def fetch_calendar_raw():
    resp = requests.get(FF_CALENDAR_URL_THIS_WEEK, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def normalize_events(raw_events: list) -> list:
    """يحول شكل بيانات Forex Factory لشكل موحّد يطابق الداشبورد."""
    normalized = []
    for ev in raw_events:
        normalized.append({
            "title": ev.get("title"),
            "country": ev.get("country"),
            "date": ev.get("date"),
            "impact": ev.get("impact"),        # High / Medium / Low
            "forecast": ev.get("forecast"),
            "previous": ev.get("previous"),
            "actual": ev.get("actual"),
        })
    return normalized


def filter_high_impact(events: list) -> list:
    return [e for e in events if (e.get("impact") or "").lower() == "high"]


def fetch_and_save():
    raw = fetch_calendar_raw()
    events = normalize_events(raw)

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "forexfactory (unofficial public feed)",
        "events": events,
        "high_impact_events": filter_high_impact(events),
    }

    out_dir = os.path.join(OUTPUT_DIR, "calendar")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "calendar_thisweek.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK] تم حفظ {path} — {len(events)} حدث ({len(payload['high_impact_events'])} عالي الأهمية)")
    return payload


if __name__ == "__main__":
    fetch_and_save()
