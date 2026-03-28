from collections import deque


DEFAULT_HISTORY_LIMIT = 200


def create_symbol_history(closes=None, rsi_values=None, limit=DEFAULT_HISTORY_LIMIT):
    closes_buffer = deque(maxlen=limit)
    rsi_buffer = deque(maxlen=limit)

    if closes:
        closes_buffer.extend(closes)

    if rsi_values:
        rsi_buffer.extend(rsi_values)

    return {
        "closes": closes_buffer,
        "rsi_values": rsi_buffer,
    }


def append_history(history, close_price, rsi_value):
    history["closes"].append(close_price)
    history["rsi_values"].append(rsi_value)


def get_history_lists(history):
    return {
        "closes": list(history["closes"]),
        "rsi_values": list(history["rsi_values"]),
    }