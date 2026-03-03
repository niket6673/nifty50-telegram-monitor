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

def is_market_open():
    now = datetime.datetime.now(IST)

    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=15, second=0)
    end = now.replace(hour=15, minute=30, second=0)

    return start <= now <= end

def get_nifty_data():
    ticker = yf.Ticker(NIFTY_SYMBOL)
    data = ticker.history(period="1d", interval="1m")

    if data.empty:
        return None

    current = data["Close"].iloc[-1]
    open_price = data["Open"].iloc[0]

    change = current - open_price
    change_pct = (change / open_price) * 100

    return current, change, change_pct

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=payload)

def main():
    if not is_market_open():
        return

    for attempt in range(3):
        try:
            result = get_nifty_data()
            if result:
                current, change, change_pct = result
                now = datetime.datetime.now(IST).strftime("%I:%M %p")

                message = f"""📊 NIFTY 50 Update

Time: {now} IST
Price: {current:.2f}
Day Change: {change:+.2f} ({change_pct:+.2f}%)
Market: Open
"""
                send_message(message)
                return
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    main()
