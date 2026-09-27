import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

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

        score = 0

        # Trend Score

        if current_price > ma50:
            score += 40

        if current_price > ma200:
            score += 40

        # RSI Sweet Spot

        if 50 <= rsi <= 70:
            score += 20

        # Trading Plan

        stop_loss = round(ma50 * 0.97, 2)

        risk_per_share = current_price - stop_loss

        if risk_per_share <= 0:
            continue

        target_price = round(
            current_price + (risk_per_share * 2),
            2
        )

        shares = int(
            100 / risk_per_share
        )

        results.append({
            "Ticker": symbol,
            "Price": round(current_price, 2),
            "MA50": round(ma50, 2),
            "MA200": round(ma200, 2),
            "RSI": round(rsi, 1),
            "Score": score,
            "Stop Loss": stop_loss,
            "Target": target_price,
            "Shares": shares
        })

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

report = pd.DataFrame(results)

if not report.empty:

    report = report.sort_values(
        by=["Score", "
