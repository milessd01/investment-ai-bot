import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os
import json
import pytz

EMAIL_SENDER = os.environ['EMAIL_SENDER']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_RECEIVER = os.environ['EMAIL_RECEIVER']

portfolio_file = "portfolio.json"
if os.path.exists(portfolio_file):
    with open(portfolio_file, "r") as f:
        portfolio = json.load(f)
else:
    portfolio = []

tickers = ['AAPL', 'INTC', 'C', 'F', 'T', 'PFE', 'GM', 'CSCO', 'BAC', 'WFC']

def get_score(info):
    pe = info.get('trailingPE')
    pb = info.get('priceToBook')
    fcf = info.get('freeCashflow')
    debt = info.get('debtToEquity')
    score = 0
    if pe and pe < 15: score += 1
    if pb and pb < 1.5: score += 1
    if fcf and fcf > 0: score += 1
    if debt and debt < 1.0: score += 1
    return score

results = []
for ticker in tickers:
    stock = yf.Ticker(ticker)
    try:
        score = get_score(stock.info)
        if score >= 3:
            results.append((ticker, score, stock.info))
    except:
        continue

results.sort(key=lambda x: x[1], reverse=True)
today = datetime.now(pytz.timezone('US/Eastern')).strftime('%B %d, %Y')
top_pick = results[0] if results else None

body = f"<h2>Undervalued Stocks - {today}</h2>"
for r in results:
    ticker, score, info = r
    body += f"<p><b>{ticker}</b> — Score: {score} <br> P/E: {info.get('trailingPE')}<br> P/B: {info.get('priceToBook')}<br> FCF: {info.get('freeCashflow')}<br> Debt/Equity: {info.get('debtToEquity')}</p>"

if top_pick:
    price = yf.Ticker(top_pick[0]).history(period="1d")['Close'].iloc[-1]
    body += f"<hr><h3>🏆 Top Pick: {top_pick[0]}</h3><p>Simulating $100 investment at ${price:.2f}</p>"
    portfolio.append({
        "ticker": top_pick[0],
        "date": today,
        "price": round(float(price), 2),
        "amount": 100
    })

with open(portfolio_file, "w") as f:
    json.dump(portfolio, f)

msg = MIMEText(body, 'html')
msg['Subject'] = f"📈 Undervalued Stock Picks - {today}"
msg['From'] = EMAIL_SENDER
msg['To'] = EMAIL_RECEIVER

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)

print("✅ Email sent.")
