from fitparse import FitFile

from src.utils import activities as au
from src.utils import fit as fu
from src.utils import google_calendar as gcu

def main():
    print("App is running.")
    service = gcu.connect_to_google_calendar()

    # Ensure Garmin Workouts calendar exists
    if not gcu.workout_calendar_exists(service):
        print("Garmin Workouts calendar does not exist. Creating...")
        gcu.create_workout_calendar(service)

    # Get latest activity
    activities_list = sorted(list(au.get_activities()), reverse=True)

    for activity in activities_list:
        fit_file = FitFile(str(activity))
        df = fu.fit_to_df(fit_file)
        activity_data = fu.extract_event_data(df)

        # Check if activity already exists in calendar
        if gcu.event_exists(
            service,
            "Garmin Workouts",
            activity_data['date'],
            activity_data['hash']
        ):
            print(f"Activity {activity} already exists in calendar.")
            continue
        # Create event in calendar
        gcu.create_activity_event(
            service,
            activity_data,
        )
        print(f"Event for {activity} created successfully.")
    print("Process completed.")


if __name__ == "__main__":
    main()
