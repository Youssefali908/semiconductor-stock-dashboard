"""Independent analysis helpers for an adjusted-close equity comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def compute_metrics(adjusted_closes: pd.DataFrame) -> dict:
    """Calculate comparable metrics from aligned adjusted daily close prices.

    The caller must supply trading dates as the index and one column per ticker.
    Rows with missing prices are intentionally excluded for fair comparisons.
    """
    prices = adjusted_closes.sort_index().dropna(how="any").astype(float)
    if prices.shape[1] < 3:
        raise ValueError("At least three company columns are required.")
    if len(prices) < 5:
        raise ValueError("Select at least five common trading sessions.")
    if (prices <= 0).any().any():
        raise ValueError("Adjusted closing prices must be positive.")

    returns = prices.pct_change(fill_method=None).dropna(how="any")
    period_return = (prices.iloc[-1] / prices.iloc[0] - 1.0) * 100.0
    volatility = returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100.0
    indexed = prices.div(prices.iloc[0]).mul(100.0)
    correlation = returns.corr()
    return {
        "prices": prices,
        "daily_returns": returns,
        "period_return_pct": period_return,
        "annualized_volatility_pct": volatility,
        "indexed": indexed,
        "correlation": correlation,
    }


def strongest_return_correlation(correlation: pd.DataFrame) -> tuple[str, str, float] | None:
    """Return the pair with the strongest absolute daily-return correlation."""
    candidates = []
    for i, first in enumerate(correlation.columns):
        for second in correlation.columns[i + 1 :]:
            value = correlation.loc[first, second]
            if pd.notna(value):
                candidates.append((str(first), str(second), float(value)))
    return max(candidates, key=lambda row: abs(row[2])) if candidates else None
