"""Review user's calendars and ensure a Garmin Workouts calendar exists."""
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
  """Load credentials from token.json or start OAuth flow."""
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # Force re-auth if the stored token does not include the required scopes.
    if not set(SCOPES).issubset(set(creds.scopes or [])):
      print("Existing token lacks required scopes, re-authenticating...")
      creds = None
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds


def list_calendars(service):
  """Return all calendars on the account."""
  calendars = []
  page_token = None
  while True:
    result = service.calendarList().list(pageToken=page_token).execute()
    calendars.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
      break
  return calendars


def ensure_garmin_calendar(service, calendars, name="Garmin Workouts"):
  """Create a Garmin Workouts calendar if it does not already exist."""
  existing = [c for c in calendars if c.get("summary") == name]
  if existing:
    print(f'"{name}" calendar already exists: {existing[0].get("id")}')
    return existing[0]

  new_calendar = (
      service.calendars()
      .insert(
          body={
              "summary": name,
              "timeZone": "UTC",
          }
      )
      .execute()
  )
  print(f'Created "{name}" calendar with id: {new_calendar.get("id")}')
  return new_calendar


def main():
  creds = get_credentials()
  try:
    service = build("calendar", "v3", credentials=creds)

    calendars = list_calendars(service)
    if calendars:
    #   print("Calendars on this account:")
    #   for cal in calendars:
    #     print(f"- {cal.get('summary')} ({cal.get('id')})")
        pass
    else:
      print("No calendars found.")

    ensure_garmin_calendar(service, calendars)

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
