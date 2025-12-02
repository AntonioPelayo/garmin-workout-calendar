# Garmin Workout Calendar

A tool that exports your Garmin activities so you can view them directly in your calendar application.

## Usage
### Data Ingestion
Connect watch to computer and using an app such as "Android File Transfer" copy the `.fit` files from `GARMIN/ACTIVITY` to `data/garmin_fit_activities/`.

Then run the ingestion script to filter for running activities and convert `.fit` files to parquet into `data/parquet_run_activities/`.
```bash
./venv/bin/python -m scripts.fit_ingestion
```

## Google Calendar Configuration
Create a Google Cloud Project in the Google Cloud Console, enable the Google Calendar API, and create OAuth 2.0 credentials.
Download the `credentials.json` file and place it in the root project directory.
Finally test the calendar setup with Google's quickstart script.
