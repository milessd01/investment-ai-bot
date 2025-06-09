import os
import smtplib
import yfinance as yf
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", EMAIL_SENDER)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CSV_FILE = "picks.csv"

def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["date", "ticker", "price"])
    df = pd.read_csv(CSV_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_summary(df):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    recent = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    if recent.empty:
        return "No picks made in the last 7 days."

    results = []
    for _, row in recent.iterrows():
        current_price = get_current_price(row["ticker"])
        if current_price is None:
            results.append((row["ticker"], row["price"], None))
        else:
            results.append((row["ticker"], row["price"], current_price))

    report_lines = ["📊 Weekly Investment Summary\n"]
    returns = []
    for ticker, original, current in results:
        if current is None:
            report_lines.append(f"{ticker}: No current data")
        else:
            change = ((current - original) / original) * 100
            returns.append(change)
            report_lines.append(f"{ticker}: {change:+.2f}% (from ${original:.2f} to ${current:.2f})")

    if returns:
        avg = sum(returns) / len(returns)
        best = max(returns)
        worst = min(returns)
        gain_count = sum(1 for r in returns if r > 0)
        loss_count = sum(1 for r in returns if r < 0)

        report_lines.append("\n📈 Summary Stats:")
        report_lines.append(f"Average Return: {avg:.2f}%")
        report_lines.append(f"Best Pick: {best:.2f}%")
        report_lines.append(f"Worst Pick: {worst:.2f}%")
        report_lines.append(f"Gainers: {gain_count} | Losers: {loss_count}")
    else:
        report_lines.append("\nNo return data available.")

    return "\n".join(report_lines)

def get_current_price(ticker):
    try:
        return yf.Ticker(ticker).info.get("regularMarketPrice")
    except:
        return None

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📬 Weekly summary email sent.")
    except Exception as e:
        print("❌ Email failed:", e)

def main():
    df = load_data()
    report = get_summary(df)
    send_email("📅 Weekly Investment Summary", report)

if __name__ == "__main__":
    main()
