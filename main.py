import pandas as pd
import talib
import yfinance as yf
import schedule
import time
import json
import requests

# Load configuration
with open('config.json') as f:
    config = json.load(f)

def get_stock_data(ticker):
    data = yf.download(ticker, period='1d', interval='1m')
    return data

def calculate_rsi(data, period):
    data['RSI'] = talib.RSI(data['Close'], timeperiod=period)
    return data

def send_telegram(message):
    url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
    payload = {'chat_id': config['chat_id'], 'text': message}
    response = requests.post(url, json=payload)
    print(response.json())

def check_signal():
    print("Checking for signals...")
    data = get_stock_data(config['ticker'])
    if data.empty:
        print("No data fetched.")
        return

    data = calculate_rsi(data, config['rsi_period'])
    latest_rsi = data['RSI'].iloc[-1]

    print(f"Latest RSI: {latest_rsi}")

    if latest_rsi < config['buy_threshold']:
        send_telegram(f"📉 BUY Signal for {config['ticker']} (RSI: {latest_rsi:.2f})")
    elif latest_rsi > config['sell_threshold']:
        send_telegram(f"📈 SELL Signal for {config['ticker']} (RSI: {latest_rsi:.2f})")
    else:
        print("No trading signal triggered.")

# Run every minute
schedule.every(1).minute.do(check_signal)

print("App started. Monitoring stock signals...")
while True:
    schedule.run_pending()
    time.sleep(10)
