import yfinance as yf
import requests
import datetime
import pytz
import os
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

NIFTY_SYMBOL = "^NSEI"
IST = pytz.timezone("Asia/Kolkata")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def is_weekend(now):
    return now.weekday() >= 5

def is_market_hours(now):
    start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return start <= now <= end

def get_intraday_data():
    ticker = yf.Ticker(NIFTY_SYMBOL)
    data = ticker.history(period="1d", interval="1m")
    return data

def main():
    now = datetime.datetime.now(IST)

    # Skip weekends completely
    if is_weekend(now):
        return

    # Fetch data
    for attempt in range(3):
        try:
            data = get_intraday_data()
            break
        except Exception:
            time.sleep(5)
    else:
        return

    # If no intraday data → likely holiday
    if data.empty:
        # Send holiday notification only during first scheduled hour (before 10 AM IST)
        if now.hour < 10:
            message = f"""📊 NIFTY 50 Update

Date: {now.strftime('%d %b %Y')}
Market Closed (Holiday)

No trading session today.
"""
            send_message(message)
        return

    # If outside market hours but weekday → do nothing
    if not is_market_hours(now):
        return

    # Normal open market update
    current = data["Close"].iloc[-1]
    open_price = data["Open"].iloc[0]

    change = current - open_price
    change_pct = (change / open_price) * 100

    message = f"""📊 NIFTY 50 Update

Time: {now.strftime('%I:%M %p')} IST
Price: {current:.2f}
Day Change: {change:+.2f} ({change_pct:+.2f}%)
Market: Open
"""

    send_message(message)

if __name__ == "__main__":
    main()
