"""Download activity .fit files from the Garmin Connect Personal API.

Files are saved to GARMIN_FIT_ACTIVITIES_PATH using the same naming the watch
uses on its own storage: the activity start in local time, YYYY-MM-DD-HH-MM-SS.fit.

Run directly with:
    ./venv/bin/python -m src.utils.garmin [--since YYYY-MM-DD]
"""
import argparse
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path

from fitparse import FitFile

from config import GARMIN_FIT_ACTIVITIES_PATH, GARMIN_PERSONAL_API_KEY

BASE_URL = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
SEARCH_PATH = "/activitylist-service/activities/search/activities"
DOWNLOAD_PATH = "/download-service/files/activity/{activity_id}"

USER_AGENT = "garmin-workout-calendar"
TIMEOUT_SECONDS = 30
PAGE_SIZE = 50
MAX_FIT_BYTES = 50 * 1024 * 1024
WATCH_FILENAME_FORMAT = "%Y-%m-%d-%H-%M-%S"


def _request(url, headers, method="GET"):
    req = urllib.request.Request(
        url, method=method, headers={"User-Agent": USER_AGENT, **headers}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return resp.read()


def get_api_key():
    """Prefer the GARMIN_PERSONAL_API_KEY env var, fall back to config.py."""
    key = os.environ.get("GARMIN_PERSONAL_API_KEY") or GARMIN_PERSONAL_API_KEY
    if not key or key.startswith("your_"):
        raise ValueError("GARMIN_PERSONAL_API_KEY is not set.")
    return key.strip()


def get_access_token(api_key):
    """Exchange a Personal API key for a bearer token (valid ~24 hours)."""
    body = _request(
        BASE_URL + TOKEN_PATH,
        {"Accept": "*/*", "Authorization": f"ApiKey {api_key}"},
        method="POST",
    )
    return body.decode("utf-8").strip()


def search_activities(token, start_date=None, end_date=None):
    """Yield activity summaries, paging through all results."""
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    start = 0
    while True:
        params = {"start": start, "limit": PAGE_SIZE}
        if start_date:
            params["startDate"] = str(start_date)
        if end_date:
            params["endDate"] = str(end_date)
        url = f"{BASE_URL}{SEARCH_PATH}?{urllib.parse.urlencode(params)}"
        page = json.loads(_request(url, headers) or b"[]")
        if not page:
            return
        yield from page
        if len(page) < PAGE_SIZE:
            return
        start += PAGE_SIZE


def download_fit_bytes(token, activity_id):
    """Return the original .fit bytes for an activity, or None if it isn't a FIT upload."""
    url = BASE_URL + DOWNLOAD_PATH.format(activity_id=int(activity_id))
    headers = {
        "Accept": "application/zip, application/x-zip-compressed, application/octet-stream",
        "Authorization": f"Bearer {token}",
    }
    try:
        content = _request(url, headers)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

    if not zipfile.is_zipfile(io.BytesIO(content)):
        # Bare FIT files start with a header containing ".FIT" at bytes 8-12
        return content if content[8:12] == b".FIT" else None

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for info in zf.infolist():
            if info.filename.lower().endswith(".fit"):
                if info.file_size > MAX_FIT_BYTES:
                    raise ValueError(f"FIT file for activity {activity_id} is too large")
                with zf.open(info) as f:
                    return f.read(MAX_FIT_BYTES + 1)[:MAX_FIT_BYTES]
    return None  # GPX/TCX or other non-FIT upload


def watch_filename(fit_bytes):
    """Build the watch-style filename from the FIT's own local start time."""
    fit = FitFile(io.BytesIO(fit_bytes))
    # The watch names files by session start_time (file_id.time_created can be 1s later)
    created = None
    for msg in fit.get_messages("session"):
        created = msg.get_value("start_time")
        break
    if created is None:
        for msg in fit.get_messages("file_id"):
            created = msg.get_value("time_created")
            break

    offset = timedelta(0)
    for msg in fit.get_messages("activity"):
        utc, local = msg.get_value("timestamp"), msg.get_value("local_timestamp")
        if utc and local:
            # The two timestamps can be written a second apart; real UTC
            # offsets are multiples of 15 minutes, so round to that.
            quarter_hours = round((local - utc).total_seconds() / 900)
            offset = timedelta(minutes=15 * quarter_hours)
        break

    if created is None:
        return None
    return (created + offset).strftime(WATCH_FILENAME_FORMAT) + ".fit"


def api_filename(activity):
    """Watch-style filename guessed from the API summary, used to skip known files."""
    start_local = activity.get("startTimeLocal")  # "YYYY-MM-DD HH:MM:SS"
    if not start_local:
        return None
    return start_local[:19].replace(" ", "-").replace(":", "-") + ".fit"


def latest_local_activity_date(directory=GARMIN_FIT_ACTIVITIES_PATH):
    """Date of the newest watch-named file, or None if the folder is empty."""
    names = sorted(p.stem for p in Path(directory).glob("*.fit"))
    for name in reversed(names):
        try:
            return date.fromisoformat(name[:10])
        except ValueError:
            continue
    return None


def sync_fit_activities(since=None, directory=GARMIN_FIT_ACTIVITIES_PATH):
    """
    Download new .fit activities from Garmin Connect into `directory`.

    :param since: Only fetch activities on/after this date. Defaults to the day
        before the newest local file, or all history if the folder is empty.
    :return: List of paths that were written.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    if since is None:
        latest = latest_local_activity_date(directory)
        since = latest - timedelta(days=1) if latest else None

    token = get_access_token(get_api_key())
    existing = {p.name for p in directory.glob("*.fit")}
    written = []

    for activity in search_activities(token, start_date=since):
        activity_id = activity.get("activityId")
        if activity_id is None or api_filename(activity) in existing:
            continue

        fit_bytes = download_fit_bytes(token, activity_id)
        if fit_bytes is None:
            print(f"Activity {activity_id} has no FIT file, skipping.")
            continue

        name = watch_filename(fit_bytes) or api_filename(activity)
        if name is None or name in existing:
            continue

        path = directory / name
        path.write_bytes(fit_bytes)
        existing.add(name)
        written.append(path)
        print(f"Downloaded {name} (activity {activity_id}).")

    print(f"Garmin sync complete: {len(written)} new file(s).")
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", type=date.fromisoformat, help="YYYY-MM-DD")
    args = parser.parse_args()
    sync_fit_activities(since=args.since)
