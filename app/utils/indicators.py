from config import RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD


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

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    return {
        "avg_gain": avg_gain,
        "avg_loss": avg_loss,
        "last_close": closes[-1],
        "last_candle_time": candle_time,
        "rsi": rsi,
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
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    state["rsi"] = rsi

    return rsi


def get_signal(rsi):
    if rsi < RSI_OVERSOLD:
        return "перепродан"
    if rsi > RSI_OVERBOUGHT:
        return "перекуплен"
    return "нейтрален"