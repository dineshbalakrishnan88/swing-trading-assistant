import yfinance as yf

ticker = yf.Ticker("NVDA")

price = ticker.history(period="1d")

print("NVIDIA latest data:")
print(price.tail())
