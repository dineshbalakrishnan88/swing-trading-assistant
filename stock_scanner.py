import yfinance as yf
import pandas as pd

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

    df = yf.download(
        symbol,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if len(df) < 200:
        continue

    current_price = float(df["Close"].iloc[-1])

    ma50 = float(df["Close"].tail(50).mean())

    ma200 = float(df["Close"].tail(200).mean())

    score = 0

    if current_price > ma50:
        score += 50

    if current_price > ma200:
        score += 50

    results.append({
        "Ticker": symbol,
        "Price": round(current_price,2),
        "MA50": round(ma50,2),
        "MA200": round(ma200,2),
        "Score": score
    })

report = pd.DataFrame(results)

report = report.sort_values(
    by="Score",
    ascending=False
)

print("\nTOP STOCKS\n")

print(report)
