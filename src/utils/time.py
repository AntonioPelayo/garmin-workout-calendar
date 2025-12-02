import pandas as pd

def elapsed_time_seconds(timestamps: pd.Series) -> pd.Series:
    """Calculate elapsed time in seconds from a series of timestamps."""
    timestamps = timestamps.dropna()
    if timestamps.empty:
        return pd.Series(dtype=float)

    timestamps = pd.to_datetime(timestamps)
    start_time = timestamps.min()
    return (timestamps - start_time).dt.total_seconds()
