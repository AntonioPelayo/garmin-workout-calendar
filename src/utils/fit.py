from typing import Union

from fitparse import FitFile
import pandas as pd

from src.utils.time import elapsed_time_seconds

def get_sport_from_fit(fit: FitFile) -> Union[str, str]:
    """Return the sport string from a FIT file, if present. Lowercased when returned."""
    sport = ''
    sub_sport = ''

    for msg in fit.get_messages('session'):
        fields = {f.name: f.value for f in msg}
        if fields.get('sport') is not None and sport == '':
            sport = str(fields['sport']).lower()
        if fields.get('sub_sport') is not None and sub_sport == '':
            sub_sport = str(fields['sub_sport']).lower()
        if sport != '' and sub_sport != '':
            break

    if sport == '' or sub_sport == '':
        for msg in fit.get_messages('sport'):
            fields = {f.name: f.value for f in msg}
            if sport == '' and fields.get('sport') is not None:
                sport = str(fields['sport']).lower()
            if sub_sport == '' and fields.get('sub_sport') is not None:
                sub_sport = str(fields['sub_sport']).lower()
            if sport != '' and sub_sport != '':
                break

    return sport, sub_sport


def parse_fit_file(fit: FitFile) -> pd.DataFrame:
    records = []

    for record in fit.get_messages("record"):
        record_data = {d.name: d.value for d in record}
        records.append(record_data)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    df = df[[col for col in df.columns if "unknown" not in col.lower()]]

    if "distance" in df.columns:
        df["distance_m"] = pd.to_numeric(df["distance"], errors="coerce")
        df["distance_mi"] = df["distance_m"] * 0.000621371
        df.drop(columns=["distance"], inplace=True)

    df["elapsed_time_s"] = elapsed_time_seconds(df["timestamp"])

    sport, sub_sport = get_sport_from_fit(fit)
    df["sport"] = sport
    df["sub_sport"] = sub_sport

    df.reset_index(drop=True, inplace=True)
    return df