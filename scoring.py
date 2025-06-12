# scoring.py (uses FMP data to improve scoring)

import yfinance as yf
from fmp_fetcher import fetch_fmp_data

# ---- Define score weights ----
WEIGHTS = {
    "pe": -0.25,
    "peg": -0.35,
    "pb": -0.2,
    "div_yield": 0.25,
    "momentum": 0.45,
    "roe": 0.3
}

# ---- Normalize individual values ----
def normalize(value, min_val, max_val):
    if value is None or value != value:
        return 0
    return max(0, min(1, (value - min_val) / (max_val - min_val)))

# ---- Score a single stock using FMP + yfinance hybrid ----
def score_stock(ticker):
    try:
        # Grab fast financials from FMP
        fmp_data = fetch_fmp_data(ticker)

        pe = fmp_data.get("pe") if fmp_data else None
        pb = fmp_data.get("priceToBookRatio") if fmp_data else None
        div_yield = fmp_data.get("lastDiv") / fmp_data.get("price") if fmp_data and fmp_data.get("price") else None
        roe = fmp_data.get("returnOnEquityTTM") if fmp_data else None

        # Fallback or extra metrics from yfinance
        yf_info = yf.Ticker(ticker).info
        peg = yf_info.get("pegRatio")

        # Normalize
        pe_score = 1 - normalize(pe, 5, 35)
        peg_score = 1 - normalize(peg, 0.5, 2.5)
        pb_score = 1 - normalize(pb, 0.5, 10)
        div_score = normalize(div_yield, 0.005, 0.05)
        roe_score = normalize(roe, 0.05, 0.3)

        # Momentum from price history
        hist = yf.Ticker(ticker).history(period="1mo")
        if len(hist) >= 2:
            momentum = (hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]
        else:
            momentum = 0
        momentum_score = normalize(momentum, -0.1, 0.2)

        # Final score
        score = (
            WEIGHTS["pe"] * pe_score +
            WEIGHTS["peg"] * peg_score +
            WEIGHTS["pb"] * pb_score +
            WEIGHTS["div_yield"] * div_score +
            WEIGHTS["momentum"] * momentum_score +
            WEIGHTS["roe"] * roe_score
        )

        return round(score * 100, 2)

    except Exception as e:
        print(f"Error scoring {ticker}: {e}")
        return None
