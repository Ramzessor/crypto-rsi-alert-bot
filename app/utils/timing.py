import time
from config import INTERVAL


def get_interval_seconds():
    interval_map = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "30m": 1800,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400,
    }

    return interval_map.get(INTERVAL)


def get_sleep_time():
    interval_seconds = get_interval_seconds()

    if interval_seconds is None:
        print(f"Неизвестный интервал: {INTERVAL}")
        return 10

    now = time.time()
    next_candle_time = ((now // interval_seconds) + 1) * interval_seconds

    buffer_seconds = 2
    sleep_time = next_candle_time - now + buffer_seconds

    return max(sleep_time, 1)
