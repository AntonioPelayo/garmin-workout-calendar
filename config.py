from pathlib import Path

# Data paths
DATA_PATH = Path("data")
GARMIN_FIT_ACTIVITIES_PATH = DATA_PATH / "garmin_fit_activities"

# Number of most recent local .fit activities to check against Google Calendar (None for all)
RECENT_ACTIVITIES_LIMIT = 10

# Garmin Personal API Key
GARMIN_PERSONAL_API_KEY = "your_garmin_personal_api_key_here"

# Google API
GOOGLE_API_SCOPES = ["https://www.googleapis.com/auth/calendar"]
GOOGLE_API_CREDENTIALS_JSON_PATH = Path("credentials.json")
GOOGLE_API_TOKEN_JSON_PATH = Path("token.json")


# Conversion constants
IMPERIAL_UNITS=True
MI_TO_KM = 1.60934
KM_TO_MI = 0.621371
FT_TO_M = 0.3048
M_TO_FT = 3.28084
