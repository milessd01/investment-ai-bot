# utils.py (for your AI investment bot, not the backtester)
import pandas as pd

HISTORY_FILE = "stock_history.csv"


def get_sp500_tickers():
    """
    Scrapes the current list of S&P 500 tickers from Wikipedia.
    Returns a list of ticker symbols like ['AAPL', 'MSFT', 'GOOGL', ...]
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Some tickers have dots (e.g., BRK.B) that yfinance wants as hyphens (BRK-B)
        return [ticker.replace(".", "-") for ticker in tickers]
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return []
