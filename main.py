# main.py (rewritten to implement smarter scoring + better data hygiene)
import os
import pandas as pd
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from scoring import score_stock

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ---- Get S&P 500 tickers ----
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        tables = pd.read_html(url)
        df = tables[0]
        return df['Symbol'].tolist()
    except Exception as e:
        print("Error fetching S&P 500 tickers:", e)
        return []

# ---- Rank stocks by score ----
def rank_stocks(tickers):
    scores = []
    for ticker in tickers:
        try:
            score = score_stock(ticker)
            if score is not None:
                scores.append((ticker, score))
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
    return sorted(scores, key=lambda x: x[1], reverse=True)

# ---- Build and send the email ----
def send_email(picks):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Top AI Stock Picks - Daily"

    html = "<h2>Top AI-Selected Stocks Today</h2><ul>"
    for ticker, score in picks:
        html += f"<li><strong>{ticker}</strong> - Score: {score:.2f}</li>"
    html += "</ul>"

    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# ---- Main Execution ----
def main():
    print("Fetching tickers...")
    tickers = get_sp500_tickers()
    print(f"Fetched {len(tickers)} tickers")

    print("Scoring tickers...")
    ranked = rank_stocks(tickers)
    top_picks = ranked[:3] if ranked else []

    if top_picks:
        print("Sending email with top picks:", top_picks)
        send_email(top_picks)
    else:
        print("No stocks scored well today.")

if __name__ == "__main__":
    main()
