from datetime import timezone
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils import hashing as hu
from config import (
    GOOGLE_API_SCOPES,
    GOOGLE_API_CREDENTIALS_JSON_PATH,
    GOOGLE_API_TOKEN_JSON_PATH,
    IMPERIAL_UNITS,
    KM_TO_MI,
    M_TO_FT
)

def load_credentials(json_path=GOOGLE_API_CREDENTIALS_JSON_PATH):
    if not json_path.exists():
        print(f"{json_path} does not exist.")
        return None
    elif GOOGLE_API_TOKEN_JSON_PATH.exists():
        creds = Credentials.from_authorized_user_file(
            GOOGLE_API_TOKEN_JSON_PATH, GOOGLE_API_SCOPES
        )
        return creds
    else:
        print("No credentials found.")
        return None


def validate_credentials(creds):
    if not creds or not creds.valid:
        print("Credentials are not valid.")
        try:
            if creds.expired and creds.refresh_token:
                print("Google API credentials expired. Refreshing...")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_API_CREDENTIALS_JSON_PATH, GOOGLE_API_SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(GOOGLE_API_TOKEN_JSON_PATH, "w") as token:
                token.write(creds.to_json())
                print("Credentials have been refreshed and saved.")
        except Exception as e:
            print(f"An error occurred while refreshing credentials: {e}")
            return False
    return True


# Google Calendar Connection Functions
def connect_to_google_calendar():
    creds = load_credentials()

    if not validate_credentials(creds):
        print("Failed to validate credentials.")
        return None

    try:
        service = build("calendar", "v3", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    return service


# Calendar Utility Functions
def get_calendar_id(service, calendar_name="Garmin Workouts"):
    calendar = workout_calendar_exists(service, calendar_name)
    if calendar:
        return calendar.get("id")
    return None


def get_calendar_events_on_date(service, calendar_id, date):
    import datetime as dt
    start_of_day = dt.datetime.combine(date, dt.time.min).isoformat() + 'Z'  # 'Z' indicates UTC time
    end_of_day = dt.datetime.combine(date, dt.time.max).isoformat() + 'Z'

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    return events


def get_or_create_calendar_id(service, calendar_name="Garmin Workouts"):
    """Return the workout calendar's ID, creating the calendar if it doesn't exist."""
    calendar_id = get_calendar_id(service, calendar_name)
    if calendar_id:
        return calendar_id
    print(f"{calendar_name} calendar does not exist. Creating...")
    return create_workout_calendar(service, calendar_name)


def event_exists(service, calendar_id, activity_date, activity_hash):
    events = get_calendar_events_on_date(service, calendar_id, activity_date)
    for event in events:
        hash = hu.get_event_hash(event)
        if hash == "":
            continue
        if hash == activity_hash:
            return True
    return False


def get_activity_type(activity_data):
    """Build a readable activity label, e.g. 'Road Run', 'Hiking', 'Strength Training'."""
    sport = activity_data['sport']
    sub_sport = activity_data['sub_sport']

    # Training sub sports already describe the activity (e.g. 'strength_training')
    if sport == 'training' and sub_sport:
        label = sub_sport
    else:
        label = f"{sub_sport} {sport}"
    return label.replace('_', ' ').strip().title()


def create_activity_event(
    service,
    activity_data,
    calendar_id,
    imperial_units=IMPERIAL_UNITS
):
    distance_km = round(activity_data['distance'] / 1000, 2)
    activity_type = get_activity_type(activity_data)
    title = f"{distance_km}km {activity_type}" if distance_km else activity_type
    description = f"Elapsed time: {activity_data['elapsed_time']}"
    description += f"<br>Elevation gain: {round(activity_data['elevation_gain'], 2)}m"

    if imperial_units:
        distance_mi = round((activity_data['distance'] / 1000) * KM_TO_MI, 2)
        title = f"{distance_mi}mi {activity_type}" if distance_mi else activity_type
        description = f"Elapsed time: {activity_data['elapsed_time']}"
        description += f"<br>Elevation gain: {round(activity_data['elevation_gain'] * M_TO_FT)}ft"
    description += f"<br>Activity hash: {activity_data['hash']}"

    try:
        create_workout_event(
            service,
            calendar_id=calendar_id,
            start_time=activity_data['start_utc'],
            end_time=activity_data['end_utc'],
            title=title,
            description=description,
            location=activity_data.get('location', ''),
            time_zone=activity_data.get('timezone', 'UTC'),
        )
    except Exception as e:
        print(f"An error occurred while creating the event: {e}")


# Workout Calendar Functions
def workout_calendar_exists(service, calendar_name="Garmin Workouts"):
    calendars = []
    page_token = None
    while True:
        result = service.calendarList().list(pageToken=page_token).execute()
        calendars.extend(result.get("items", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    existing = [c for c in calendars if c.get("summary") == calendar_name]
    return existing[0] if existing else None


def create_workout_calendar(service, calendar_name="Garmin Workouts"):
    new_calendar = (
        service.calendars()
        .insert(
            body={
                "summary": calendar_name,
                "timeZone": "UTC",
            }
        )
        .execute()
    )
    print(
        f'Created "{calendar_name}" calendar with id: {new_calendar.get("id")}'
    )
    return new_calendar.get("id")

def to_zone_iso(utc_time, time_zone):
    """ISO timestamp with offset in `time_zone`, from a UTC (naive or aware) datetime."""
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    return utc_time.astimezone(ZoneInfo(time_zone)).isoformat()


def create_workout_event(
    service,
    calendar_id,
    start_time,
    end_time,
    title="",
    description="",
    location="",
    time_zone="UTC",
):
    """Create an event; start/end are UTC (naive or aware), shown in `time_zone`."""
    event_body = {
        "summary": title,
        "start": {"dateTime": to_zone_iso(start_time, time_zone), "timeZone": time_zone},
        "end": {"dateTime": to_zone_iso(end_time, time_zone), "timeZone": time_zone},
        "description": description
    }
    if location:
        event_body["location"] = location

    event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    print(f'Event created: {event.get("htmlLink")}')
