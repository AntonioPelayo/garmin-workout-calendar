#!/bin/sh
# Download new Garmin .fit activities. Pass --since YYYY-MM-DD to backfill.
./venv/bin/python -m src.utils.garmin "$@"
