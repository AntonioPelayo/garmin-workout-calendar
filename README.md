# Garmin Workout Calendar

A tool that exports your Garmin activities so you can view them directly in your calendar application.

## Usage
The app is accessed via command line as:
```bash
./venv/bin/python -m src.app
```

### Adding Workout Data
Connect watch to computer and using an app such as "Android File Transfer" copy the `.fit` files from `GARMIN/ACTIVITY` to `data/garmin_fit_activities/`.

### Google Calendar Configuration
Create a Google Cloud Project in the Google Cloud Console, enable the Google Calendar API, and create OAuth 2.0 credentials.

Download the `credentials.json` file and place it in the root project directory.

Test the calendar API setup with Google's Python quickstart script within the root directory.

**You MUST delete** the `.readonly` text from the `SCOPES` variable in the quickstart script, a `token.json` file will be created after the successful run.
Link: https://developers.google.com/workspace/calendar/api/quickstart/python
