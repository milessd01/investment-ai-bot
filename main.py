import os
import yfinance as yf
import pandas as pd
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from utils import get_sp500_tickers, HISTORY_FILE

TOP_N = 3

def score_stock(ticker):
    try:
        info = yf.Ticker(ticker).info
        pe = info.get("trailingPE")
        if pe and pe > 0:
            return 1 / pe
        return None
    except Exception:
        return None

def send_email(subject, body, sender, password, receiver):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE, parse_dates=["date"])
    else:
        return pd.DataFrame(columns=["date", "ticker", "score"])

def save_history(new_entries):
    df = load_history()
    df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def get_followups(df, days_ago):
    cutoff = datetime.now() - timedelta(days=days_ago)
    return df[df["date"] == cutoff.date()]

def main():
    tickers = get_sp500_tickers()
    results = []

    for ticker in tickers:
        score = score_stock(ticker)
        if score is not None:
            results.append((ticker, score))

    top = sorted(results, key=lambda x: x[1], reverse=True)[:TOP_N]
    today = datetime.now().date()

    # Save today's picks
    history_entries = [{"date": today, "ticker": ticker, "score": score} for ticker, score in top]
    save_history(history_entries)

    # Compose daily email
    body = f"📅 Investment Picks for {today}:\n\n"
    for i, (ticker, score) in enumerate(top, 1):
        body += f"{i}. {ticker} – Score: {score:.2f}\n"

    # Compose follow-up emails
    history = load_history()
    week_followups = get_followups(history, 7)
    month_followups = get_followups(history, 30)

    if not week_followups.empty:
        body += "\n📬 1-Week Follow-Ups:\n"
        for _, row in week_followups.iterrows():
            body += f"- {row['ticker']} (scored {row['score']:.2f} on {row['date']})\n"

    if not month_followups.empty:
        body += "\n📬 1-Month Follow-Ups:\n"
        for _, row in month_followups.iterrows():
            body += f"- {row['ticker']} (scored {row['score']:.2f} on {row['date']})\n"

    # Send the email
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("❌ Missing environment variables for email credentials.")
        return

    subject = f"📈 Daily Investment Picks – {today}"
    send_email(subject, body, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER)
    print("✅ Email sent!")

if __name__ == "__main__":
    main()
