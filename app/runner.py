import time

from config import SYMBOLS, RSI_PERIOD
from app.state import RuntimeState
from app.history import create_symbol_history
from app.services.binance import (
    get_candles,
    get_closed_candles,
    get_closes_from_candles,
    get_last_closed_candle_time,
)
from app.services.processor import catch_up
from app.indicators.rsi import (
    initialize_rsi_state,
    get_rsi_signal,
    calculate_rsi_series,
)
from app.utils.timing import get_sleep_time


def startup_sync(symbols, rsi_states, last_signals, history_buffers):
    print("Запуск startup sync...")

    for symbol in symbols:
        data = get_candles(symbol)

        if data is None:
            print(f"{symbol} | не удалось получить данные для инициализации")
            continue

        closed_candles = get_closed_candles(data)

        if len(closed_candles) < RSI_PERIOD + 1:
            print(f"{symbol} | недостаточно закрытых свечей для инициализации")
            continue

        closes = get_closes_from_candles(closed_candles)
        last_candle_time = get_last_closed_candle_time(closed_candles)

        state = initialize_rsi_state(
            closes=closes,
            candle_time=last_candle_time,
        )

        if state is None:
            print(f"{symbol} | не удалось инициализировать RSI state")
            continue

        rsi_series = calculate_rsi_series(closes)
        filtered_rsi_series = [value for value in rsi_series if value is not None]

        history_buffers[symbol] = create_symbol_history(
            closes=closes,
            rsi_values=filtered_rsi_series,
        )

        rsi_states[symbol] = state

        current_signal = get_rsi_signal(state["rsi"])
        last_signals[symbol] = current_signal

        print(
            f"{symbol} | состояние RSI инициализировано | "
            f"RSI: {state['rsi']:.2f} | сигнал: {current_signal}"
        )


def run_live_loop(symbols, rsi_states, last_signals, history_buffers):
    print("Переход в live-режим...")

    while True:
        sleep_time = get_sleep_time()
        print(f"Спим {sleep_time:.2f} сек до следующей свечи")
        time.sleep(sleep_time)

        catch_up(symbols, rsi_states, last_signals, history_buffers)


def run_bot():
    state = RuntimeState(
        rsi_states={},
        last_signals={},
        history_buffers={},
    )

    startup_sync(
        symbols=SYMBOLS,
        rsi_states=state.rsi_states,
        last_signals=state.last_signals,
        history_buffers=state.history_buffers,
    )

    if not state.rsi_states:
        print("Не удалось инициализировать ни один символ. Бот остановлен.")
        return

    active_symbols = list(state.rsi_states.keys())

    run_live_loop(
        symbols=active_symbols,
        rsi_states=state.rsi_states,
        last_signals=state.last_signals,
        history_buffers=state.history_buffers,
    )