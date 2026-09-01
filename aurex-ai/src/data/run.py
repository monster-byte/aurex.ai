"""
نقطة تشغيل موحدة لطبقة البيانات: يسحب الأسعار + التقويم الاقتصادي معاً
تشغيل: python -m src.data.run
"""

from .price_fetcher import fetch_all, save_snapshot
from .calendar_fetcher import fetch_and_save as fetch_calendar


def main():
    print("=== AUREX AI | Data Layer Run ===")

    print("\n[1/2] جلب بيانات الأسعار (yfinance)...")
    prices = fetch_all(timeframe="1D")
    save_snapshot(prices, timeframe="1D")

    print("\n[2/2] جلب التقويم الاقتصادي (Forex Factory)...")
    fetch_calendar()

    print("\n=== انتهى ✅ ===")


if __name__ == "__main__":
    main()
