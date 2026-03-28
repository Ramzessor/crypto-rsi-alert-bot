import time
from app.utils.indicators import update_rsi_state, get_signal
from app.services.binance import get_candles, get_last_closed_candle_info
from app.services.telegram import send_message


def process_symbol(symbol, rsi_states, last_signals):
    data = get_candles(symbol)

    if data is None:
        print(f"{symbol} | не удалось получить данные")
        return False

    candle_time, close_price = get_last_closed_candle_info(data)
    if candle_time is None:
        print(f"{symbol} | недостаточно данных по свечам")
        return False

    state = rsi_states.get(symbol)
    if state is None:
        print(f"{symbol} | состояние RSI не найдено")
        return False

    if candle_time == state["last_candle_time"]:
        print(
            f"{symbol} | новая свеча еще не появилась | "
            f"api_candle_time={candle_time} | state_time={state['last_candle_time']}"
        )
        return False

    rsi = update_rsi_state(state, close_price, candle_time)
    signal = get_signal(rsi)

    print(f"{symbol} | RSI: {rsi:.2f} | signal: {signal}")

    last_signal = last_signals.get(symbol)

    if signal != last_signal:
        if signal != "нейтрален":
            message = f"{symbol}\nRSI: {rsi:.2f}\nСигнал: {signal}"
            send_message(message)

        last_signals[symbol] = signal

    return True


def catch_up(symbols, rsi_states, last_signals, timeout=30):
    start_time = time.time()
    processed_symbols = set()

    while time.time() - start_time < timeout:
        print(f"Catch-up loop | уже обновлены: {sorted(processed_symbols)}")
        for symbol in symbols:
            if symbol in processed_symbols:
                continue

            is_processed = process_symbol(symbol, rsi_states, last_signals)

            if is_processed:
                processed_symbols.add(symbol)

        if len(processed_symbols) == len(symbols):
            print("Все символы обновлены")
            return

        time.sleep(1)

    missing = list(set(symbols) - processed_symbols)
    print(f"Catch-up завершён по таймауту. Не обновились: {missing}")
