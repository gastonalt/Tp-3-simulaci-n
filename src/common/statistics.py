"""Statistics helpers for independent simulation replications."""

from __future__ import annotations

import math


def mean(values: list[float]) -> float | None:
    clean_values = _clean(values)
    if not clean_values:
        return None
    return sum(clean_values) / len(clean_values)


def sample_stdev(values: list[float]) -> float | None:
    clean_values = _clean(values)
    n = len(clean_values)
    if n < 2:
        return None

    avg = sum(clean_values) / n
    variance = sum((value - avg) ** 2 for value in clean_values) / (n - 1)
    return math.sqrt(variance)


def confidence_interval_half_width(
    values: list[float],
    confidence: float = 0.95,
) -> float | None:
    if confidence != 0.95:
        raise ValueError("only 95 percent confidence intervals are supported")

    clean_values = _clean(values)
    n = len(clean_values)
    if n < 2:
        return None

    stdev = sample_stdev(clean_values)
    if stdev is None:
        return None

    return t_critical_975(n - 1) * stdev / math.sqrt(n)


def t_critical_975(degrees_of_freedom: int) -> float:
    """Return two-sided 95 percent t critical value.

    Exact table values are included for the small samples used in the TP. For
    larger sample sizes, the normal approximation is enough for reporting.
    """

    table = {
        1: 12.706,
        2: 4.303,
        3: 3.182,
        4: 2.776,
        5: 2.571,
        6: 2.447,
        7: 2.365,
        8: 2.306,
        9: 2.262,
        10: 2.228,
        11: 2.201,
        12: 2.179,
        13: 2.160,
        14: 2.145,
        15: 2.131,
        16: 2.120,
        17: 2.110,
        18: 2.101,
        19: 2.093,
        20: 2.086,
        21: 2.080,
        22: 2.074,
        23: 2.069,
        24: 2.064,
        25: 2.060,
        26: 2.056,
        27: 2.052,
        28: 2.048,
        29: 2.045,
        30: 2.042,
    }
    return table.get(degrees_of_freedom, 1.96)


def percent_error(observed: float | None, expected: float | None) -> float | None:
    if observed is None or expected is None:
        return None
    if abs(expected) < 1e-12:
        return 0.0 if abs(observed) < 1e-12 else None
    return 100.0 * (observed - expected) / expected


def _clean(values: list[float]) -> list[float]:
    return [
        value
        for value in values
        if value is not None and not math.isnan(value)
    ]
