from pathlib import Path

# Data paths
DATA_PATH = Path("data")
GARMIN_FIT_ACTIVITIES_PATH = DATA_PATH / "garmin_fit_activities"
PARQUET_ACTIVITIES_PATH = DATA_PATH / "parquet_activities"


# Google API
GOOGLE_API_SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_API_CREDENTIALS_JSON_PATH = Path("credentials.json")
GOOGLE_API_TOKEN_JSON_PATH = Path("token.json")


# Conversion constants
M_TO_MI_MULTIPLIER = 0.000621371
