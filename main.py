import requests
import time
import os
from dotenv import load_dotenv
from config import (
    SYMBOLS,
    INTERVAL,
    LIMIT,
    RSI_PERIOD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    SLEEP_TIME,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


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


def initialize_rsi_state(closes, candle_time):
    if len(closes) < RSI_PERIOD + 1:
        return None

    changes = []

    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        changes.append(change)

    gains = []
    losses = []

    for change in changes:
        if change > 0:
            gains.append(change)
            losses.append(0)
        elif change < 0:
            gains.append(0)
            losses.append(abs(change))
        else:
            gains.append(0)
            losses.append(0)

    avg_gain = sum(gains[:RSI_PERIOD]) / RSI_PERIOD
    avg_loss = sum(losses[:RSI_PERIOD]) / RSI_PERIOD

    for i in range(RSI_PERIOD, len(gains)):
        avg_gain = ((avg_gain * (RSI_PERIOD - 1)) + gains[i]) / RSI_PERIOD
        avg_loss = ((avg_loss * (RSI_PERIOD - 1)) + losses[i]) / RSI_PERIOD

    return {
        "avg_gain": avg_gain,
        "avg_loss": avg_loss,
        "last_close": closes[-1],
        "last_candle_time": candle_time,
    }


def update_rsi_state(state, new_close, new_candle_time):
    change = new_close - state["last_close"]

    if change > 0:
        gain = change
        loss = 0
    elif change < 0:
        gain = 0
        loss = abs(change)
    else:
        gain = 0
        loss = 0

    avg_gain = ((state["avg_gain"] * (RSI_PERIOD - 1)) + gain) / RSI_PERIOD
    avg_loss = ((state["avg_loss"] * (RSI_PERIOD - 1)) + loss) / RSI_PERIOD

    state["avg_gain"] = avg_gain
    state["avg_loss"] = avg_loss
    state["last_close"] = new_close
    state["last_candle_time"] = new_candle_time

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_signal(rsi):
    if rsi < RSI_OVERSOLD:
        return "перепродан"
    elif rsi > RSI_OVERBOUGHT:
        return "перекуплен"
    else:
        return "нейтрален"


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Ошибка Telegram: {response.status_code} | {responce.text}")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


def main():
    print("Bot started...")
    rsi_states = {}
    last_signals = {}

    for symbol in SYMBOLS:
        data = get_candles(symbol)

        if data is None:
            print(f"{symbol} | не удалось получить данные")
            continue

        closes = get_closes(data)
        candle_time, close_price = get_last_candle_info(data)
        if candle_time is None:
            print(f"{symbol} | недостаточно данных по свечам")
            continue

        state = initialize_rsi_state(closes, candle_time)

        if state is not None:
            rsi_states[symbol] = state
            last_signals[symbol] = None
            print(f"{symbol} | состояние RSI инициализировано")
        else:
            print(f"{symbol} | не удалось инициилизировать RSI")

    while True:
        try:
            for symbol in SYMBOLS:
                data = get_candles(symbol)

                if data is None:
                    print(f"{symbol} | не удалось получить данные")
                    continue

                candle_time, close_price = get_last_candle_info(data)
                if candle_time is None:
                    print(f"{symbol} | недостаточно данных по свечам")
                    continue

                state = rsi_states.get(symbol)
                if state is None:
                    continue

                if candle_time == state["last_candle_time"]:
                    print(f"{symbol} | свеча ещё не закрылась")
                    continue

                rsi = update_rsi_state(state, close_price, candle_time)
                signal = get_signal(rsi)

                print(f"{symbol} | RSI: {rsi:.2f} | signal: {signal}")

                last_signal = last_signals.get(symbol)

                if signal != last_signal:
                    if signal != "нейтрален":
                        message = f"{symbol}\nRSI: {rsi:.2f}\nСигнал: {signal}"
                        send_message(message)

                    last_signals[symbol] = signal
        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
