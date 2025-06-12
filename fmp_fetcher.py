# fmp_fetcher.py
import os
import requests

def fetch_fmp_data(ticker):
    api_key = os.getenv("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and data:
            return data[0]
        return None
    except Exception as e:
        print(f"FMP fetch failed for {ticker}: {e}")
        return None
