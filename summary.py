import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pytz

EMAIL_SENDER = os.environ['EMAIL_SENDER']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_RECEIVER = os.environ['EMAIL_RECEIVER']

portfolio_file = "portfolio.json"

if not os.path.exists(portfolio_file):
    print("No portfolio to summarize.")
    exit()

with open(portfolio_file, "r") as f:
    portfolio = json.load(f)

if not portfolio:
    print("Portfolio is empty.")
    exit()

# Generate summary report
body = "<h2>📊 Weekly Brokerage Summary</h2>"
total_invested = 0
tickers = []

for entry in portfolio:
    tickers.append(entry["ticker"])
    total_invested += entry["amount"]

unique_tickers = list(set(tickers))
body += f"<p>Total invested: ${total_invested:.2f}</p>"
body += f"<p>Number of investments: {len(portfolio)}</p>"
body += "<p>Unique tickers:</p><ul>"

for t in unique_tickers:
    body += f"<li>{t}</li>"
body += "</ul>"

# Email setup
today = datetime.now(pytz.timezone('US/Eastern')).strftime('%B %d, %Y')
msg = MIMEText(body, 'html')
msg['Subject'] = f"📈 Weekly Brokerage Summary - {today}"
msg['From'] = EMAIL_SENDER
msg['To'] = EMAIL_RECEIVER

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)

print("✅ Weekly summary sent.")
