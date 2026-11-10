# Garmin Workout Calendar

A tool that exports your recorded Garmin activities to your calendar application so that you can see how your training fits into real life.

## Usage
After setup to sync and add the events to your calendar in one step, run
```bash
./bin/sync_garmin.sh && ./bin/upload_workouts.sh
```

## Adding Workout Data
### Garmin Personal API (recommended)
Create a key at https://connect.garmin.com/app/settings/personalApiToken and export it (or set `GARMIN_PERSONAL_API_KEY` in `config.py`, but don't commit it):
```bash
export GARMIN_PERSONAL_API_KEY='your-key'
./venv/bin/python -m src.utils.garmin               # new activities since your newest local file
./venv/bin/python -m src.utils.garmin --since 2025-01-01
```
Files are saved to `data/garmin_fit_activities/` with the same names the watch uses (`YYYY-MM-DD-HH-MM-SS.fit`, local start time).

### From the watch
Connect watch to computer and using an app such as "Android File Transfer" copy the `.fit` files from `GARMIN/ACTIVITY` to `data/garmin_fit_activities/`.

## Google Calendar Configuration
Create a Google Cloud Project in the Google Cloud Console, enable the Google Calendar API, and create OAuth 2.0 credentials.

Download the `credentials.json` file and place it in the root project directory.

Test the calendar API setup with Google's Python quickstart script within the root directory.

**You MUST delete** the `.readonly` text from the `SCOPES` variable in the quickstart script, a `token.json` file will be created after the successful run.
Link: https://developers.google.com/workspace/calendar/api/quickstart/python

#### Expired Tokens
If your `token.json` expires, delete it and re-run the quickstart script to generate a new one.
