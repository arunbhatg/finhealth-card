"""Shared helper utilities."""

import random
import string


def score_to_grade(score: float) -> str:
    from src.utils.constants import GRADE_THRESHOLDS

    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "Poor"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def yoy_growth(series: list[float]) -> float:
    if len(series) < 2:
        return 0.0
    base = series[-13] if len(series) >= 13 else series[0]
    current = series[-1]
    if base == 0:
        return 0.0
    return (current - base) / abs(base) * 100


def avg_recent(series: list[float], months: int = 3) -> float:
    if not series:
        return 0.0
    return sum(series[-months:]) / min(len(series), months)


def compliance_rate(statuses: list[str], good: set[str] | None = None) -> float:
    if not statuses:
        return 0.0
    good = good or {"filed", "paid", "on_time"}
    return sum(1 for s in statuses if s in good) / len(statuses)


def generate_gstin(state_code: str = "27", rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    chars = string.ascii_uppercase + string.digits
    body = "".join(rng.choices(chars, k=10))
    return f"{state_code}{body}1Z{rng.choice(chars)}"


def generate_pan(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    chars = string.ascii_uppercase
    digits = string.digits
    return (
        "".join(rng.choices(chars, k=5))
        + "".join(rng.choices(digits, k=4))
        + rng.choice(chars)
    )
