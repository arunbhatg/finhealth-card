"""Shared helpers for time-series charts."""

from __future__ import annotations

from calendar import month_abbr
from datetime import date

import pandas as pd


def month_axis_labels(count: int) -> list[str]:
    """Month labels oldest → newest for `count` periods ending this month."""
    d = date.today().replace(day=1)
    labels: list[str] = []
    for _ in range(count):
        labels.append(f"{month_abbr[d.month]} '{d.year % 100:02d}")
        if d.month == 1:
            d = d.replace(year=d.year - 1, month=12)
        else:
            d = d.replace(month=d.month - 1)
    return list(reversed(labels))


def timeseries_df(values: list, *, y_name: str = "Value") -> pd.DataFrame:
    """Build a Month × value dataframe aligned to the latest N observations."""
    vals = list(values)
    labels = month_axis_labels(len(vals))
    return pd.DataFrame({"Month": labels, y_name: vals})
