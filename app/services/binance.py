import requests
from config import INTERVAL, LIMIT


def get_candles(symbol):
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    )

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


def get_closed_candles(data):
    if not data or len(data) < 2:
        return []

    return data[:-1]


def get_last_closed_candle_info(data):
    closed_candles = get_closed_candles(data)

    if not closed_candles:
        return None, None

    last_closed_candle = closed_candles[-1]
    candle_time = last_closed_candle[0]
    close_price = float(last_closed_candle[4])

    return candle_time, close_price


def get_closes_from_candles(candles):
    closes = []

    for candle in candles:
        close_price = float(candle[4])
        closes.append(close_price)

    return closes


def get_last_closed_candle_time(candles):
    if not candles:
        return None

    return candles[-1][0]
