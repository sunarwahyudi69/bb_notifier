import requests
import time
from datetime import datetime
import pytz

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
    url = f'https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&apikey={API_KEY}&outputsize=30'
    response = requests.get(url)
    data = response.json()
    if 'values' not in data:
        print("Gagal ambil data:", data)
        return []
    return list(reversed(data['values']))

def calculate_bb(data, period=20, dev=2):
    closes = [float(item['close']) for item in data]
    if len(closes) < period:
        return None, None, None
    ma = sum(closes[-period:]) / period
    std = (sum((x - ma) ** 2 for x in closes[-period:]) / period) ** 0.5
    upper = ma + dev * std
    lower = ma - dev * std
    return closes[-1], upper, lower

last_checked = None
utc = pytz.utc

while True:
    candles = get_candle_data()
    if not candles:
        time.sleep(60)
        continue

    last_candle = candles[-1]
    candle_time = datetime.strptime(last_candle['datetime'], '%Y-%m-%d %H:%M:%S')
    candle_time = utc.localize(candle_time)

    now = datetime.utcnow().replace(second=0, microsecond=0)
    now = utc.localize(now)

    # Pastikan candle sudah close
    if now <= candle_time:
        print(f"{datetime.now()} - Sudah dicek / Candle belum close")
        time.sleep(30)
        continue

    if last_checked == candle_time:
        print(f"{datetime.now()} - Sudah dicek")
        time.sleep(30)
        continue

    close, upper, lower = calculate_bb(candles)
    msg = None
    if close > upper:
        msg = f"ALERT: Close di atas Upper BB\nClose: {close}\nUpper: {upper}\nTime: {last_candle['datetime']}"
    elif close < lower:
        msg = f"ALERT: Close di bawah Lower BB\nClose: {close}\nLower: {lower}\nTime: {last_candle['datetime']}"

    if msg:
        send_alert(msg)
        print("Dikirim:", msg)
    else:
        print(f"{datetime.now()} - Tidak ada sinyal")

    last_checked = candle_time
    time.sleep(60)
