import requests
import time
from datetime import datetime

# Konfigurasi API dan Telegram
API_KEY = '7e47b4e228294356a43b62da3d46da8f'
SYMBOL = 'EUR/USD'
INTERVAL = '5min'

TOKEN = '7078254247:AAGWzhzoSR5isKgY2ksShimtJek6rtarXfc'
CHAT_ID = '7503139684'

def send_alert(message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=data)
    except:
        print("Gagal kirim notifikasi")

def get_candle_data():
    try:
        url = f'https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&apikey={API_KEY}&outputsize=20'
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'values' not in data:
            print("Gagal ambil data:", data)
            return []
        return list(reversed(data['values']))
    except Exception as e:
        print("Error ambil data:", e)
        return []

def calculate_bb(data, period=20, dev=2):
    try:
        closes = [float(item['close']) for item in data]
        if len(closes) < period:
            return None, None, None
        ma = sum(closes[-period:]) / period
        std = (sum((x - ma) ** 2 for x in closes[-period:]) / period) ** 0.5
        upper = ma + dev * std
        lower = ma - dev * std
        return closes[-1], upper, lower
    except Exception as e:
        print("Error hitung BB:", e)
        return None, None, None

last_time = None

while True:
    candles = get_candle_data()
    if not candles:
        print(f"{datetime.now()} - Tidak ada data candle")
        time.sleep(60)
        continue

    close_price, upper_band, lower_band = calculate_bb(candles)
    candle_time = candles[-1]['datetime'] if candles else None

    if close_price is None or upper_band is None or lower_band is None:
        print(f"{datetime.now()} - Gagal hitung BB")
        time.sleep(60)
        continue

    if last_time == candle_time:
        print(f"{datetime.now()} - Sudah dicek")
    else:
        msg = None
        if close_price > upper_band:
            msg = f"ALERT: Close di atas Upper BB\nClose: {close_price}\nUpper: {upper_band}\nTime: {candle_time}"
        elif close_price < lower_band:
            msg = f"ALERT: Close di bawah Lower BB\nClose: {close_price}\nLower: {lower_band}\nTime: {candle_time}"

        if msg:
            send_alert(msg)
            print("Dikirim:", msg)
        else:
            print(f"{datetime.now()} - Tidak ada sinyal")

        last_time = candle_time

    time.sleep(60)
