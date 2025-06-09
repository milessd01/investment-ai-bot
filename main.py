import os
import smtplib
import yfinance as yf
import requests
import pandas as pd
from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", EMAIL_SENDER)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Load full S&P 500 tickers
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url).text
    df_list = pd.read_html(StringIO(html))
    sp500_table = df_list[0]
    return sp500_table['Symbol'].tolist()

# Smarter undervalued stock screening
def find_undervalued_stocks(tickers):
    undervalued = []

    print("\n🔍 Screening all S&P 500 companies...")
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            pe = info.get("trailingPE")
            peg = info.get("pegRatio")
            pb = info.get("priceToBook")
            div_yield = info.get("dividendYield")

            # Log what we're seeing
            print(f"{symbol}: PE={pe}, PEG={peg}, PB={pb}, Div={div_yield}")

            # Screening criteria (loosened for more matches)
            if (
                pe and pe < 25 and
                peg and peg < 2 and
                pb and pb < 4 and
                div_yield and div_yield > 0.005  # > 0.5%
            ):
                summary = (
                    f"{symbol} (PE: {pe:.2f}, PEG: {peg:.2f}, "
                    f"P/B: {pb:.2f}, Div Yield: {div_yield*100:.2f}%)"
                )
                undervalued.append(summary)

        except Exception as e:
            print(f"⚠️ {symbol} skipped: {e}")

    print(f"\n✅ Screening complete. {len(undervalued)} undervalued stocks found.")
    for pick in undervalued[:5]:
        print(" -", pick)

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
        print("📬 Email sent successfully.")
    except Exception as e:
        print("❌ Email failed:", e)

def main():
    print("📈 Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers.")

    undervalued = find_undervalued_stocks(tickers)

    subject = "📊 Daily Undervalued S&P 500 Stocks"
    body = "Here are today's undervalued picks:\n\n" + "\n".join(undervalued or ["None found"])

    send_email(subject, body)

if __name__ == "__main__":
    main()
