from fitparse import FitFile
import pandas as pd

from src.utils.time import elapsed_time_seconds

def parse_fit_file(fit: FitFile) -> pd.DataFrame:
    records = []

    for record in fit.get_messages("record"):
        record_data = {d.name: d.value for d in record}
        records.append(record_data)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    if "distance" in df.columns:
        df["distance_m"] = pd.to_numeric(df["distance"], errors="coerce")
        df["distance_mi"] = df["distance_m"] * 0.000621371
        df.drop(columns=["distance"], inplace=True)

    df["elapsed_time_s"] = elapsed_time_seconds(df["timestamp"])

    df.reset_index(drop=True, inplace=True)
    return pd.DataFrame(records)