from dataclasses import dataclass


@dataclass
class Pivot:
    index: int
    value: float


@dataclass
class DivergenceResult:
    signal: str | None
    price_pivots: list[Pivot]
    rsi_pivots: list[Pivot]
    message: str | None = None


def find_pivot_lows(values, left=2, right=2):
    pivots = []

    for i in range(left, len(values) - right):
        current_value = values[i]

        left_side = values[i - left:i]
        right_side = values[i + 1:i + right + 1]

        if all(current_value < x for x in left_side) and all(
            current_value < x for x in right_side
        ):
            pivots.append(Pivot(index=i, value=current_value))

    return pivots


def find_pivot_highs(values, left=2, right=2):
    pivots = []

    for i in range(left, len(values) - right):
        current_value = values[i]

        left_side = values[i - left:i]
        right_side = values[i + 1:i + right + 1]

        if all(current_value > x for x in left_side) and all(
            current_value > x for x in right_side
        ):
            pivots.append(Pivot(index=i, value=current_value))

    return pivots


def match_pivots(price_pivots, rsi_pivots, max_distance=3):
    matched = []
    used_rsi_indexes = set()

    for price_pivot in price_pivots:
        closest_rsi = None
        min_distance = float("inf")

        for rsi_pivot in rsi_pivots:
            if rsi_pivot.index in used_rsi_indexes:
                continue

            distance = abs(price_pivot.index - rsi_pivot.index)

            if distance <= max_distance and distance < min_distance:
                min_distance = distance
                closest_rsi = rsi_pivot

        if closest_rsi is not None:
            matched.append((price_pivot, closest_rsi))
            used_rsi_indexes.add(closest_rsi.index)

    return matched


def detect_bullish_divergence(price_lows, rsi_lows):
    matched = match_pivots(price_lows, rsi_lows)

    if len(matched) < 2:
        return None

    (price_prev, rsi_prev), (price_last, rsi_last) = matched[-2:]

    price_makes_lower_low = price_last.value < price_prev.value
    rsi_makes_higher_low = rsi_last.value > rsi_prev.value

    if price_makes_lower_low and rsi_makes_higher_low:
        return DivergenceResult(
            signal="bullish",
            price_pivots=[price_prev, price_last],
            rsi_pivots=[rsi_prev, rsi_last],
            message="Найдена бычья дивергенция",
        )

    return None


def detect_bearish_divergence(price_highs, rsi_highs):
    matched = match_pivots(price_highs, rsi_highs)

    if len(matched) < 2:
        return None

    (price_prev, rsi_prev), (price_last, rsi_last) = matched[-2:]

    price_makes_higher_high = price_last.value > price_prev.value
    rsi_makes_lower_high = rsi_last.value < rsi_prev.value

    if price_makes_higher_high and rsi_makes_lower_high:
        return DivergenceResult(
            signal="bearish",
            price_pivots=[price_prev, price_last],
            rsi_pivots=[rsi_prev, rsi_last],
            message="Найдена медвежья дивергенция",
        )

    return None


def analyze_divergence(closes, rsi_values, left=2, right=2):
    if len(closes) < left + right + 1 or len(rsi_values) < left + right + 1:
        return DivergenceResult(
            signal=None,
            price_pivots=[],
            rsi_pivots=[],
            message=None,
        )

    filtered_rsi_values = [value for value in rsi_values if value is not None]

    if len(filtered_rsi_values) < left + right + 1:
        return DivergenceResult(
            signal=None,
            price_pivots=[],
            rsi_pivots=[],
            message=None,
        )

    price_lows = find_pivot_lows(closes, left=left, right=right)
    price_highs = find_pivot_highs(closes, left=left, right=right)

    rsi_lows = find_pivot_lows(filtered_rsi_values, left=left, right=right)
    rsi_highs = find_pivot_highs(filtered_rsi_values, left=left, right=right)

    bullish_result = detect_bullish_divergence(price_lows, rsi_lows)
    if bullish_result is not None:
        return bullish_result

    bearish_result = detect_bearish_divergence(price_highs, rsi_highs)
    if bearish_result is not None:
        return bearish_result

    return DivergenceResult(
        signal=None,
        price_pivots=[],
        rsi_pivots=[],
        message=None,
    )