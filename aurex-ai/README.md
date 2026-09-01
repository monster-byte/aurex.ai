# AUREX AI — Data Layer (المرحلة 1)

هاي أول طبقة من محرك AUREX AI: **طبقة البيانات**.

## الفكرة
- `src/data/price_fetcher.py` → يسحب شموع وأسعار NASDAQ-100 index/futures + AAPL/MSFT/NVDA/AMZN + VXN/DXY/US10Y عبر **yfinance**.
- `src/data/calendar_fetcher.py` → يسحب التقويم الاقتصادي (CPI, NFP, Fed...) من **Forex Factory** (JSON عام).
- `src/data/run.py` → يشغل الاثنين معاً ويحفظ النتائج في `data/prices/` و `data/calendar/`.
- `.github/workflows/fetch-data.yml` → يشغّل كل شي تلقائياً كل 15 دقيقة أيام التداول عبر GitHub Actions، ويحفظ (commit) النتائج بالريبو نفسه — بدون سيرفر خارجي.

## التشغيل يدوياً (لتجربته محلياً قبل الرفع)
```bash
pip install -r requirements.txt
python -m src.data.run
```

## بعد الرفع على GitHub
1. أنشئ ريبو جديد وارفع هاي الملفات.
2. من تبويب **Actions** بالريبو، فعّل الـ workflow (أو شغّله يدوياً أول مرة عبر "Run workflow").
3. البيانات رح تنحفظ وتتحدث تلقائياً بمجلد `data/`.

## ⚠️ ملاحظة مهمة عن مصدر Forex Factory
الرابط المستخدم (`ff_calendar_thisweek.json`) هو **feed عام غير رسمي** شائع الاستخدام بمشاريع مفتوحة المصدر، مش API رسمي مدعوم من الشركة. يعني:
- ممكن يتغير شكله أو يتوقف بدون إشعار.
- إذا احتجت مصدر أكثر استقراراً لاحقاً لنفس البيانات (معدل الفائدة، CPI، NFP...)، **FRED API** (من البنك الفيدرالي، مجاني ورسمي) بديل ممتاز وأثبت.

## الخطوة الجاية
بعد ما تتأكد إن سحب البيانات شغال تمام عندك، ننتقل للمرحلة 2: **محرك الإشارة (AI Signal & Confirmation)** — حساب الـ Confirmation Score والـ Trade Probability من نفس البيانات الجاية من هاي الطبقة.
