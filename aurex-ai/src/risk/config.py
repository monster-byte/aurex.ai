"""
AUREX AI - Risk & Position Sizing Config
"""

# رأس المال الافتراضي (Account Equity)
ACCOUNT_EQUITY = 100_000.0

# نسبة المخاطرة المسموحة بكل صفقة (Risk Per Trade)
RISK_PER_TRADE_PCT = 0.01  # 1%

# نسبة الميزانية اليومية القصوى للمخاطرة (Daily Risk Budget)
DAILY_RISK_BUDGET_PCT = 0.0125  # 1.25%

# وقف الخسارة كنسبة ثابتة من سعر الدخول
STOP_LOSS_PCT = 0.01  # 1%

# مضاعفات وقف الخسارة لتحديد أهداف الربح (Risk:Reward)
TP1_RR_MULTIPLE = 1.5
TP2_RR_MULTIPLE = 3.0

# مواصفات عقد Micro E-mini Nasdaq-100 (MNQ)
MICRO_NQ_MULTIPLIER = 2.0

# رمز المؤشر المرجعي لحساب VaR والتقلب
INDEX_SYMBOL = "^NDX"
MARKET_SYMBOL = "^GSPC"

LOOKBACK_DAYS = "1y"
VAR_CONFIDENCE = 0.95

OUTPUT_PATH = "data/risk/risk_snapshot.json"
