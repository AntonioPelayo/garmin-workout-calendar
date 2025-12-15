from src.utils import activities as au
from src.utils import google_calendar as gcu
from config import (
    GARMIN_FIT_ACTIVITIES_PATH,
)


def main():
    print("App is running.")

    service = gcu.connect_to_google_calendar()
    if not gcu.workout_calendar_exists(service):
        print("Garmin Workouts calendar does not exist. Creating...")
        gcu.create_workout_calendar(service)

    activities_list = au.get_activities()
    print(f"Found {len(list(activities_list))} activities in {GARMIN_FIT_ACTIVITIES_PATH}")

    latest_activity = sorted(list(activities_list))
    print(f"Latest activity: {latest_activity[-1]}")
    start, end = au.activity_start_and_end(latest_activity[-1])
    print(f"Start time: {start}\nEnd time: {end}")

    gcu.create_workout_event(
        service,
        calendar_id=gcu.get_calendar_id(service),
        start_time=start,
        end_time=end,
        summary="summary",
        description="description"
    )


if __name__ == "__main__":
    main()
