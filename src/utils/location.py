"""Offline reverse geocoding of an activity's start point to 'City, ST'."""
import pandas as pd

SEMICIRCLES_TO_DEGREES = 180 / 2**31

US_STATE_ABBREVIATIONS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "Washington, D.C.": "DC", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def start_coordinates(df: pd.DataFrame):
    """First valid (lat, lon) in degrees from a FIT record DataFrame, or None."""
    if "position_lat" not in df or "position_long" not in df:
        return None
    points = df[["position_lat", "position_long"]].dropna()
    if points.empty:
        return None
    lat, lon = points.iloc[0]
    return float(lat) * SEMICIRCLES_TO_DEGREES, float(lon) * SEMICIRCLES_TO_DEGREES


def format_location(place: dict) -> str:
    """'City, ST' in the US, 'City, Region' (or 'City, CC') elsewhere."""
    city, region, country = place.get("name", ""), place.get("admin1", ""), place.get("cc", "")
    if country == "US":
        region = US_STATE_ABBREVIATIONS.get(region, region)
    region = region or country
    return f"{city}, {region}" if city and region else city or region


def start_location(df: pd.DataFrame) -> str:
    """Nearest town to the activity's start, or '' for indoor/no-GPS activities."""
    coords = start_coordinates(df)
    if coords is None:
        return ""
    import reverse_geocoder as rg  # lazy: loads its city dataset on first use

    # mode=1 is single-process; the default multiprocess mode is slower for one point
    place = rg.search([coords], mode=1, verbose=False)[0]
    return format_location(place)
