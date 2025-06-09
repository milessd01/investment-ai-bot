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
    ranked_candidates = []

    print("\n🔍 Screening all S&P 500 companies...")
    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            pe = info.get("trailingPE")
            peg = info.get("pegRatio")
            pb = info.get("priceToBook")
            div_yield = info.get("dividendYield")

            print(f"{symbol}: PE={pe}, PEG={peg}, PB={pb}, Div={div_yield}")

            # Save for ranking fallback
            ranked_candidates.append({
                "symbol": symbol,
                "pe": pe if pe else float("inf"),
                "peg": peg if peg else float("inf"),
                "pb": pb if pb else float("inf"),
                "div": div_yield if div_yield else 0.0
            })

            # Primary screen
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

    if undervalued:
        print(f"\n✅ Found {len(undervalued)} undervalued stocks.")
        return undervalued

    print("\n⚠️ No stocks met all criteria. Choosing best available alternatives...")

    # Sort ranked candidates by PEG, then PE, then highest dividend
    best_alternatives = sorted(
        ranked_candidates,
        key=lambda x: (x["peg"], x["pe"], -x["div"])
    )[:10]

    fallback_summaries = [
        f"{c['symbol']} (PE: {c['pe']:.2f}, PEG: {c['peg']:.2f}, "
        f"P/B: {c['pb']:.2f}, Div Yield: {c['div']*100:.2f}%)"
        for c in best_alternatives
    ]

    return fallback_summaries

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

    picks = find_undervalued_stocks(tickers)

    subject = "📊 Daily Investment Picks: Undervalued or Best Available"
    body = "Here are today's best investment picks:\n\n" + "\n".join(picks)

    send_email(subject, body)

if __name__ == "__main__":
    main()
