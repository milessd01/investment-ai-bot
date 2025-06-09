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

def load_picks():
    if not os.path.exists(CSV_FILE):
        print("⚠️ No picks.csv file found.")
        return pd.DataFrame(columns=["date", "ticker", "price"])
    return pd.read_csv(CSV_FILE)

def get_followup_targets(df, days):
    target_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    return df[df["date"] == target_date]

def get_current_price(ticker):
    try:
        return yf.Ticker(ticker).info.get("regularMarketPrice")
    except:
        return None

def format_report(df, days):
    if df.empty:
        return f"No tracked picks found from {days} days ago."

    lines = [f"📊 {days}-Day Performance Report\n"]
    for _, row in df.iterrows():
        current_price = get_current_price(row["ticker"])
        if current_price is None:
            lines.append(f"{row['ticker']}: price unavailable")
            continue
        start_price = row["price"]
        change = ((current_price - start_price) / start_price) * 100
        lines.append(f"{row['ticker']}: {change:+.2f}% (from ${start_price:.2f} to ${current_price:.2f})")

    return "\n".join(lines)

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
        print("📬 Follow-up email sent.")
    except Exception as e:
        print("❌ Email failed:", e)

def main():
    df = load_picks()
    if df.empty:
        return

    week_report = format_report(get_followup_targets(df, 7), 7)
    month_report = format_report(get_followup_targets(df, 30), 30)

    full_report = week_report + "\n\n" + month_report
    send_email("📈 Investment Follow-Up Report", full_report)

if __name__ == "__main__":
    main()
