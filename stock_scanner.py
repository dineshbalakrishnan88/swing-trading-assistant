import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from datetime import datetime

# =====================================
# SETTINGS
# =====================================

MAX_RISK_PER_TRADE = 100
MAX_STOCKS = 5

# =====================================
# MARKET REGIME
# =====================================

print("Checking Market Regime...")

market_ok = True

for index_symbol in ["SPY", "QQQ"]:

    df = yf.download(
        index_symbol,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    close = df["Close"].squeeze()

    current = float(close.iloc[-1])

    ma200 = float(close.tail(200).mean())

    if current < ma200:
        market_ok = False

if not market_ok:

    print("Market regime is BEARISH")

    report = pd.DataFrame({
        "Message": [
            "NO TRADES - BEARISH MARKET REGIME"
        ]
    })

    report.to_excel(
        "weekly_watchlist.xlsx",
        index=False
    )

    raise SystemExit()

print("Market regime is BULLISH")

# =====================================
# LOAD SP500
# =====================================

sp500_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

sp500 = pd.read_csv(sp500_url)

stocks = sp500["Symbol"].tolist()

print(f"Loaded {len(stocks)} stocks")

# =====================================
# BUILD SECTOR STRENGTH TABLE
# =====================================

sector_strength = {}

for _, row in sp500.iterrows():

    try:

        symbol = str(
            row["Symbol"]
        ).replace(".", "-")

        sector = row["Sector"]

        stock = yf.Ticker(symbol)

        hist = stock.history(
            period="6mo"
        )

        if len(hist) < 50:
            continue

        perf = (
            hist["Close"].iloc[-1]
            /
            hist["Close"].iloc[0]
            - 1
        ) * 100

        sector_strength.setdefault(
            sector,
            []
        ).append(perf)

    except:
        pass

sector_scores = {}

for sector, values in sector_strength.items():

    if len(values) > 0:

        sector_scores[sector] = (
            sum(values)
            /
            len(values)
        )

# =====================================
# SPY RELATIVE STRENGTH
# =====================================

spy = yf.download(
    "SPY",
    period="6mo",
    auto_adjust=True,
    progress=False
)

spy_return = (
    spy["Close"].iloc[-1]
    /
    spy["Close"].iloc[0]
    - 1
) * 100

# =====================================
# MAIN SCAN
# =====================================

results = []

for _, row in sp500.iterrows():

    symbol = str(
        row["Symbol"]
    ).replace(".", "-")

    sector = row["Sector"]

    print(f"Scanning {symbol}")

    try:

        stock = yf.Ticker(symbol)

        info = stock.info

        revenue_growth = info.get(
            "revenueGrowth"
        )

        earnings_growth = info.get(
            "earningsGrowth"
        )

        profit_margin = info.get(
            "profitMargins"
        )

        market_cap = info.get(
            "marketCap"
        )

        earnings_date = info.get(
            "earningsTimestamp"
        )

        # ==================
        # FUNDAMENTALS
        # ==================

        if revenue_growth is None:
            continue

        if earnings_growth is None:
            continue

        if profit_margin is None:
            continue

        if market_cap is None:
            continue

        if revenue_growth < 0.15:
            continue

        if earnings_growth < 0.15:
            continue

        if profit_margin < 0.10:
            continue

        if market_cap < 10000000000:
            continue

        # ==================
        # EARNINGS FILTER
        # ==================

        if earnings_date:

            earnings_date = datetime.fromtimestamp(
                earnings_date
            )

            days_to_earnings = (
                earnings_date -
                datetime.now()
            ).days

            if 0 <= days_to_earnings <= 14:
                continue

        # ==================
        # PRICE DATA
        # ==================

        df = yf.download(
            symbol,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 200:
            continue

        close = df["Close"].squeeze()

        current_price = float(
            close.iloc[-1]
        )

        ma50 = float(
            close.tail(50).mean()
        )

        ma200 = float(
            close.tail(200).mean()
        )
