import numpy as np
import pandas as pd

def elapsed_seconds(timestamps: pd.Series) -> pd.Series:
    """Compute seconds elapsed from a series of timestamps."""
    timestamps = pd.to_datetime(timestamps, errors='coerce')
    t0 = timestamps.dropna().min()
    if pd.isna(t0):
        return pd.Series([np.nan] * len(timestamps))
    return (timestamps.max() - t0).total_seconds()


def hours_to_hhmmss(hours: float) -> str:
    """Convert decimal hours to an hh:mm:ss string."""
    total_seconds = int(hours * 3600)
    hours_component = total_seconds // 3600
    minutes_component = (total_seconds % 3600) // 60
    seconds_component = total_seconds % 60
    return f"{hours_component:d}:{minutes_component:02d}:{seconds_component:02d}"


def seconds_to_hours(seconds: float) -> float:
    """Convert seconds to decimal hours."""
    return seconds / 3600.0 if not np.isnan(seconds) else float("nan")