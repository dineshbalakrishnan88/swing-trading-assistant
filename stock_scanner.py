import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

MAX_RISK_PER_TRADE = 100
MAX_STOCKS = 5

print("Loading S&P500 stocks...")

sp500_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

sp500 = pd.read_csv(sp500_url)

stocks = sp500["Symbol"].tolist()

results = []

for symbol in stocks:

    symbol = str(symbol).replace(".", "-")

    print(f"Scanning {symbol}...")

    try:

        stock = yf.Ticker(symbol)

        info = stock.info

        revenue_growth = info.get(
            "revenueGrowth",
            None
        )

        earnings_growth = info.get(
            "earningsGrowth",
            None
        )

        profit_margin = info.get(
            "profitMargins",
            None
        )

        market_cap = info.get(
            "marketCap",
            None
        )

        if (
            revenue_growth is None or
            earnings_growth is None or
            profit_margin is None or
            market_cap is None
        ):
            continue

        if revenue_growth < 0.10:
            continue

        if earnings_growth < 0.10:
            continue

        if profit_margin <= 0:
            continue

        if market_cap < 10000000000:
            continue

        df = yf.download(
            symbol,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if len(df) < 200:
            continue

        close = df["Close"].squeeze()

        current_price = float(close.iloc[-1])

        ma50 = float(close.tail(50).mean())

        ma200 = float(close.tail(200).mean())

        rsi = float(
            RSIIndicator(close).rsi().iloc[-1]
        )

        if current_price <= ma50:
            continue

        if current_price <= ma200:
            continue

        if not (50 <= rsi <= 70):
            continue

        score = 100

        rating = "ELITE"

        buy_zone = round(
            ma50 * 1.02,
            2
        )

        stop_loss = round(
            ma50 * 0.97,
            2
        )

        risk_per_share = (
            current_price - stop_loss
        )

        if risk_per_share <= 0:
            continue

        target_price = round(
            current_price +
            (risk_per_share * 2),
            2
        )

        shares = max(
            1,
            int(
                MAX_RISK_PER_TRADE /
                risk_per_share
            )
        )

        results.append({

            "Ticker": symbol,

            "Rating": rating,

            "Score": score,

            "Price": round(
                current_price,
                2
            ),

            "Revenue Growth %": round(
                revenue_growth * 100,
                1
            ),

            "Earnings Growth %": round(
                earnings_growth * 100,
                1
            ),

            "Profit Margin %": round(
                profit_margin * 100,
                1
            ),

            "RSI": round(
                rsi,
                1
            ),

            "Stop Loss": stop_loss,

            "Target": target_price,

            "Shares": shares

        })

    except Exception as e:

        print(
            f"Error processing {symbol}: {e}"
        )

report = pd.DataFrame(results)

if report.empty:

    report = pd.DataFrame({
        "Message": [
            "NO HIGH-CONVICTION TRADES THIS WEEK"
        ]
    })

else:

    report = report.sort_values(
        by=[
            "Revenue Growth %",
            "Earnings Growth %"
        ],
        ascending=False
    )

    report = report.head(MAX_STOCKS)

    report.insert(
        0,
        "Rank",
        range(
            1,
            len(report) + 1
        )
    )

report.to_excel(
    "weekly_watchlist.xlsx",
    index=False
)

print(report)

print(
    "\nHigh Conviction Report Created"
)
