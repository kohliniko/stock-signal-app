# Stock Signal App

import pandas as pd
import talib
import yfinance as yf
import schedule
import time
import json
import requests

# Load configuration
with open('config.json', 'r') as file:
    config = json.load(file)

TICKER = config['ticker']
RSI_PERIOD = config['rsi_period']
BUY_THRESHOLD = config['buy_threshold']
SELL_THRESHOLD = config['sell_threshold']
TELEGRAM_TOKEN = config['telegram_token']
CHAT_ID = config['chat_id']


def get_stock_data(ticker):
    data = yf.download(ticker, period='7d', interval='1m')
    return data


def calculate_signals(data):
    data['RSI'] = talib.RSI(data['Close'], timeperiod=RSI_PERIOD)
    buy_signal = data['RSI'] < BUY_THRESHOLD
    sell_signal = data['RSI'] > SELL_THRESHOLD
    return buy_signal, sell_signal


def send_notification(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, json=payload)
        print(f'Notification sent: {message}')
    except Exception as e:
        print(f'Failed to send notification: {e}')


def job():
    stock_data = get_stock_data(TICKER)
    buy, sell = calculate_signals(stock_data)
    if buy.iloc[-1]:
        send_notification(f'Buy Signal for {TICKER}')
    elif sell.iloc[-1]:
        send_notification(f'Sell Signal for {TICKER}')


schedule.every(1).minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

# Configuration file (config.json) template:
# {
#     "ticker": "AAPL",
#     "rsi_period": 14,
#     "buy_threshold": 30,
#     "sell_threshold": 70,
#     "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
#     "chat_id": "YOUR_CHAT_ID"
# }

# Requirements file (requirements.txt):
# pandas
# yfinance
# ta-lib
# schedule
# requests
