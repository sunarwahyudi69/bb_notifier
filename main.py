import requests
import time
from datetime import datetime
import pytz

# Konfigurasi
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
    except Exception as e:
        print("Gagal kirim notifikasi:", e)

def get_candle_data():
    try:
        url = f'https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&apikey={API_KEY}&outputsize=25'
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
    closes = [float(item['close']) for item in data]
    if len(closes) < period + 1:
        return None, None, None
    ma = sum(closes[-period-1:-1]) / period
    std = (sum((x - ma) ** 2 for x in closes[-period-1:-1]) / period) ** 0.5
    upper = ma + dev * std
    lower = ma - dev * std
    return closes[-2], upper, lower  # candle[-2] = last closed

def main():
    last_checked = None

    while True:
        candles = get_candle_data()
        if len(candles) < 3:
            time.sleep(60)
            continue

        closed_candle = candles[-2]  # candle yang sudah close
        latest_candle = candles[-1]  # candle yang masih terbentuk
        candle_time_str = closed_candle['datetime']

        # Hanya cek jika candle terakhir berbeda waktu dengan closed candle
        if closed_candle['datetime'] == latest_candle['datetime']:
            print(f"{datetime.now()} - Candle belum close (masih sama dengan current candle)")
            time.sleep(60)
            continue

        if last_checked == candle_time_str:
            print(f"{datetime.now()} - Sudah dicek")
        else:
            close_price, upper_band, lower_band = calculate_bb(candles)
            msg = None
            if close_price > upper_band:
                msg = f"ALERT: Close DI ATAS Upper BB\nClose: {close_price}\nUpper: {upper_band}\nTime: {candle_time_str}"
            elif close_price < lower_band:
                msg = f"ALERT: Close DI BAWAH Lower BB\nClose: {close_price}\nLower: {lower_band}\nTime: {candle_time_str}"

            if msg:
                send_alert(msg)
                print("Dikirim:", msg)
            else:
                print(f"{datetime.now()} - Tidak ada sinyal")

            last_checked = candle_time_str

        time.sleep(60)

if __name__ == "__main__":
    main()
