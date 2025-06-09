import os
import smtplib
import yfinance as yf
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = EMAIL_SENDER  # send to self

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Load full S&P 500 tickers
def get_sp500_tickers():
    import requests
    import pandas as pd
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url).text
    df_list = pd.read_html(html)
    sp500_table = df_list[0]
    return sp500_table['Symbol'].tolist()

# Placeholder undervalued stock screening (replace with real logic later)
def find_undervalued_stocks(tickers):
    undervalued = []
    for symbol in tickers[:20]:  # limit for now to avoid overload
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            pe = info.get("trailingPE")
            if pe and pe < 15:  # simple value filter
                undervalued.append(f"{symbol} (PE: {pe})")
        except Exception as e:
            print(f"Failed {symbol}: {e}")
    return undervalued

# Send an email report
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
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Email failed:", e)

def main():
    print("📈 Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers.")

    print("🔍 Screening for undervalued stocks...")
    undervalued = find_undervalued_stocks(tickers)

    subject = "📊 Daily Undervalued S&P 500 Stocks"
    body = "Here are today's undervalued picks:\n\n" + "\n".join(undervalued or ["None found"])

    print("📧 Sending email...")
    send_email(subject, body)

if __name__ == "__main__":
    main()
