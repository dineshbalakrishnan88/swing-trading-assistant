import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

MAX_RISK_PER_TRADE = 100

stocks = [
    "NVDA",
    "PLTR",
    "CRWD",
    "PANW",
    "MRVL",
    "MSFT",
    "META",
    "AMD",
    "AVGO",
    "AAPL"
]

results = []

for symbol in stocks:

    print(f"Scanning {symbol}...")

    try:

        df = yf.download(
            symbol,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            continue

        close = df["Close"].squeeze()

        current_price = float(close.iloc[-1])

        ma50 = float(close.tail(50).mean())

        ma200 = float(close.tail(200).mean())

        rsi = float(
            RSIIndicator(close).rsi().iloc[-1]
        )

        # ==================
        # SCORING
        # ==================

        score = 0

        if current_price > ma50:
            score += 40

        if current_price > ma200:
            score += 40

        if 50 <= rsi <= 70:
            score += 20

        # ==================
        # RATING
        # ==================

        if score >= 100:
            rating = "A+"

        elif score >= 80:
            rating = "A"

        elif score >= 60:
            rating = "B"

        else:
            rating = "Avoid"

        # ==================
        # TRADE PLAN
        # ==================

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
            current_price + (risk_per_share * 2),
            2
        )

        shares = int(
            MAX_RISK_PER_TRADE /
            risk_per_share
        )

        risk_reward = round(
            (target_price - current_price)
            /
            (current_price - stop_loss),
            2
        )

        results.append({

            "Ticker": symbol,

            "Rating": rating,

            "Price": round(
                current_price,
                2
            ),

            "Buy Zone": buy_zone,

            "MA50": round(
                ma50,
                2
            ),

            "MA200": round(
                ma200,
                2
            ),

            "RSI": round(
                rsi,
                1
            ),

            "Score": score,

            "Stop Loss": stop_loss,

            "Target": target_price,

            "Shares": shares,

            "Risk/Reward": risk_reward

        })

    except Exception as e:

        print(
            f"Error processing {symbol}: {e}"
        )

# ==================
# REPORT
# ==================

report = pd.DataFrame(results)

if not report.empty:

    report = report.sort_values(
        by=["Score", "RSI"],
        ascending=[False, True]
    )

    print("\n===== TOP STOCKS =====\n")

    print(
        report.to_string(
            index=False
        )
    )

    report.to_excel(
        "weekly_watchlist.xlsx",
        index=False
    )

    print(
        "\nExcel report created"
    )

else:

    print(
        "No stocks processed."
    )
