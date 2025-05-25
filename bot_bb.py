import time
from datetime import datetime
import requests
import pandas as pd
import numpy as np
import yfinance as yf

# Telegram config
BOT_TOKEN = 'isi_token_bot_anda'
CHAT_ID = 'isi_chat_id_anda'

# Fungsi kirim pesan
def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Gagal kirim pesan:", e)

# Inisialisasi
last_time = None

while True:
    try:
        # Ambil data EURUSD TF 5m
        data = yf.download("EURUSD=X", interval="5m", period="1d")
        if data.empty:
            print(f"{datetime.now()} - Tidak ada sinyal (data kosong)")
            time.sleep(60)
            continue

        close = data['Close']
        candle_time = str(close.index[-1])

        if candle_time == last_time:
            print(f"{datetime.now()} - Sudah dicek")
            time.sleep(60)
            continue

        # Hitung Bollinger Bands
        sma = close.rolling(window=20).mean()
        std = close.rolling(window=20).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        close_price = close.iloc[-1]

        msg = None
        if close_price > upper_band.iloc[-1]:
            msg = f"ALERT: Close di atas Upper BB\nClose: {close_price}\nUpper: {upper_band.iloc[-1]}\nTime: {candle_time}"
        elif close_price < lower_band.iloc[-1]:
            msg = f"ALERT: Close di bawah Lower BB\nClose: {close_price}\nLower: {lower_band.iloc[-1]}\nTime: {candle_time}"

        if msg:
            send_alert(msg)
            print("Dikirim:", msg)
        else:
            print(f"{datetime.now()} - Tidak ada sinyal")

        last_time = candle_time
        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
