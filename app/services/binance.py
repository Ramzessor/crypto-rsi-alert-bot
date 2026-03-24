import requests
from config import INTERVAL, LIMIT


def get_candles(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"HTTP ошибка {symbol}: {response.status_code}")
            return None

        data = response.json()

        if not isinstance(data, list):
            print(f"Ошибка Binance для {symbol}: {data}")
            return None

        return data

    except Exception as e:
        print(f"Ошибка запроса для {symbol}: {e}")
        return None


def get_last_candle_info(data):
    if len(data) < 2:
        return None, None

    last_closed_candle = data[-2]
    candle_time = last_closed_candle[0]
    close_price = float(last_closed_candle[4])
    return candle_time, close_price


def get_closes(data):
    closes = []

    for candle in data:
        close_price = float(candle[4])
        closes.append(close_price)

    return closes
