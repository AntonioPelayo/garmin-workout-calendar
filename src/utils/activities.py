from fitparse import FitFile

from config import (
    GARMIN_FIT_ACTIVITIES_PATH,
)


def get_activities():
    if not GARMIN_FIT_ACTIVITIES_PATH.exists():
        print(f"{GARMIN_FIT_ACTIVITIES_PATH} does not exist.")
        return []
    return GARMIN_FIT_ACTIVITIES_PATH.glob("*.fit")


def activity_start_and_end(activity_path):
    if type(activity_path) is not str:
        activity_path = str(activity_path)

    fitfile = FitFile(activity_path)
    start_time = None
    end_time = None

    for record in fitfile.get_messages("record"):
        for data in record:
            if data.name == "timestamp":
                timestamp = data.value
                if start_time is None:
                    start_time = timestamp
                end_time = timestamp

    return start_time, end_time
