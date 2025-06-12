import os
import yfinance as yf
from datetime import datetime
from utils import get_sp500_tickers

# Optional: Set a scoring threshold or top N
TOP_N = 5

def score_stock(ticker):
    """
    Simple scoring function: inverse of P/E ratio
    """
    try:
        info = yf.Ticker(ticker).info
        pe_ratio = info.get("trailingPE")
        if pe_ratio and pe_ratio > 0:
            return 1 / pe_ratio
        return None
    except Exception:
        return None

def main():
    print("📊 Scanning S&P 500 for best investment ideas...\n")
    tickers = get_sp500_tickers()
    results = []

    for ticker in tickers:
        score = score_stock(ticker)
        if score is not None:
            results.append((ticker, score))

    if not results:
        print("⚠️ No valid scores found.")
        return

    top = sorted(results, key=lambda x: x[1], reverse=True)[:TOP_N]

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Date: {today}")
    print(f"📈 Top {TOP_N} Investment Picks:\n")
    for ticker, score in top:
        print(f"{ticker} - Score: {score:.2f}")

if __name__ == "__main__":
    main()
