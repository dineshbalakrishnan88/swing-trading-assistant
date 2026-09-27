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

    print(f"Scanning {symbol}...")

    df = yf.download(
        symbol,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        continue

    try:
        close = df["Close"].squeeze()

        current_price = float(close.iloc[-1])
        ma50 = float(close.tail(50).mean())
        ma200 = float(close.tail(200).mean())

        score = 0

        if current_price > ma50:
            score += 50

        if current_price > ma200:
            score += 50

        results.append({
            "Ticker": symbol,
            "Price": round(current_price, 2),
            "MA50": round(ma50, 2),
            "MA200": round(ma200, 2),
            "Score": score
        })

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

report = pd.DataFrame(results)

if not report.empty:

    report = report.sort_values(
        by="Score",
        ascending=False
    )

    print("\n===== TOP STOCKS =====\n")
    print(report.to_string(index=False))

    report.to_excel(
        "weekly_watchlist.xlsx",
        index=False
    )

    print("\nExcel report created")

else:
    print("No stocks processed.")
