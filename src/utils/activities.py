from fitparse import FitFile

from config import (
    GARMIN_FIT_ACTIVITIES_PATH,
)


def get_fit_activities(sorted=True, reversed=True, limit=10):
    """
    Retrieve FIT activities from the configured directory.

    :param sorted: Sort activities, useful if dates are in filenames
    :param reversed: Most recent first if True
    :param limit: Limit number of activities returned or None for all
    """
    if not GARMIN_FIT_ACTIVITIES_PATH.exists():
        print(f"{GARMIN_FIT_ACTIVITIES_PATH} does not exist.")
        return []

    activities = list(GARMIN_FIT_ACTIVITIES_PATH.glob("*.fit"))

    if sorted:
        activities.sort(reverse=reversed)

    return activities[:limit]


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
