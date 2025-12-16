from fitparse import FitFile

from src.utils import activities as au
from src.utils import fit as fu
from src.utils import google_calendar as gcu
from config import (
    IMPERIAL_UNITS,
    KM_TO_MI,
    M_TO_FT
)


def main():
    print("App is running.")

    service = gcu.connect_to_google_calendar()
    if not gcu.workout_calendar_exists(service):
        print("Garmin Workouts calendar does not exist. Creating...")
        gcu.create_workout_calendar(service)

    activities_list = list(au.get_activities())
    latest_activity = sorted(activities_list)[-1]
    fit_file = FitFile(str(latest_activity))
    df = fu.fit_to_df(fit_file)

    activity_info = fu.extract_event_data(df)
    activity_hash = gcu.create_activity_hash(
        activity_info['start_utc'],
        activity_info['elapsed_time'],
        activity_info['sport'],
        activity_info['distance'],
    )

    # Prettyfy event details
    distance = round(activity_info['distance'] / 1000, 2)
    activity_type = f"{activity_info['sub_sport'].capitalize()} {activity_info['sport'].capitalize()}"
    title = f"{distance}km {activity_type}"
    description = f"Elapsed time: {activity_info['elapsed_time']}"
    description += f"<br>Elevation gain: {round(activity_info['elevation_gain'], 2)}m"

    if IMPERIAL_UNITS:
        distance= round((activity_info['distance'] / 1000) * KM_TO_MI, 2)
        title = f"{distance}mi {activity_type}"
        description = f"Elapsed time: {activity_info['elapsed_time']}"
        description += f"<br>Elevation gain: {round(activity_info['elevation_gain'] * M_TO_FT)}ft"

    description += f"<br>Activity hash: {activity_hash}"

    gcu.create_workout_event(
        service,
        calendar_id=gcu.get_calendar_id(service),
        start_time=activity_info['start_utc'],
        end_time=activity_info['end_utc'],
        title=title,
        description=description
    )


if __name__ == "__main__":
    main()
