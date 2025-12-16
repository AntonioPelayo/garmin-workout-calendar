from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    GOOGLE_API_SCOPES,
    GOOGLE_API_CREDENTIALS_JSON_PATH,
    GOOGLE_API_TOKEN_JSON_PATH
)


def create_activity_hash(
    start_utc,
    elapsed_time,
    sport,
    distance,
):
    from hashlib import sha1

    return sha1(f"{start_utc}|{elapsed_time}|{sport}|{distance}".encode("utf-8")).hexdigest()


def connect_to_google_calendar():
    if not GOOGLE_API_CREDENTIALS_JSON_PATH.exists():
        print(f"{GOOGLE_API_CREDENTIALS_JSON_PATH} does not exist.")
        return
    elif GOOGLE_API_TOKEN_JSON_PATH.exists():
        creds = Credentials.from_authorized_user_file(
            GOOGLE_API_TOKEN_JSON_PATH, GOOGLE_API_SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_API_CREDENTIALS_JSON_PATH, GOOGLE_API_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_API_TOKEN_JSON_PATH, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")

    return service


def get_calendar_id(service, calendar_name="Garmin Workouts"):
    calendar = workout_calendar_exists(service, calendar_name)
    if calendar:
        return calendar.get("id")
    return None


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

def create_workout_event(
    service,
    calendar_id,
    start_time,
    end_time,
    title="",
    description="",
):
    event_body = {
        "summary": title,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
        "description": description
    }

    event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    print(f'Event created: {event.get("htmlLink")}')
