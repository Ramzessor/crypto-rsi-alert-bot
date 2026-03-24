import time
from config import SYMBOLS
from app.state import RuntimeState
from app.utils.timing import get_sleep_time
from app.utils.indicators import initialize_rsi_state
from app.services.binance import (
    get_candles,
    get_last_candle_info,
    get_closes,
)
from app.services.processor import catch_up


def run_bot():
    print("Bot started...")
    state = RuntimeState()

    for symbol in SYMBOLS:
        data = get_candles(symbol)

        if data is None:
            print(f"{symbol} | не удалось получить данные")
            continue

        closes = get_closes(data)
        candle_time, _ = get_last_candle_info(data)

        if candle_time is None:
            print(f"{symbol} | недостаточно данных по свечам")
            continue

        rsi_state = initialize_rsi_state(closes, candle_time)

        if rsi_state is not None:
            state.rsi_states[symbol] = rsi_state
            state.last_signals[symbol] = None
            print(f"{symbol} | состояние RSI инициализировано")
        else:
            print(f"{symbol} | не удалось инициализировать RSI")

    while True:
        try:
            sleep_time = get_sleep_time()
            print(f"Спим {sleep_time:.2f} сек до следующей свечи")
            time.sleep(sleep_time)

            catch_up(SYMBOLS, state.rsi_states, state.last_signals)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
