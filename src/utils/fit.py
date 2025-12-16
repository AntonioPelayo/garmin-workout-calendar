from typing import Union

from fitparse import FitFile
import pandas as pd

from src.utils import time as tu

EXPECTED_FIT_COLUMNS = [
    'accumulated_power', # Watts
    'activity_type', # String 'running'
    'cadence', # RPM
    'distance', # Meters
    'enhanced_altitude', # Meters
    'enhanced_speed', # Meters per second
    'fractional_cadence', # RPM
    'heart_rate', # BPM
    'position_lat', # Degrees in semicircles
    'position_long', # Degrees in semicircles
    'power', # Watts
    'stance_time', # Milliseconds
    'stance_time_balance',
    'stance_time_percent',
    'step_length', # Millimeters
    'temperature', # Celsius
    'timestamp', # YYYY-MM-DD HH:MM:SS in UTC
    'vertical_oscillation', # Millimeters
    'vertical_ratio', # Percent
    'unknown_107', 'unknown_134', 'unknown_135', 'unknown_136',
    'unknown_137', 'unknown_138', 'unknown_140', 'unknown_143',
    'unknown_87', 'unknown_90',
    # teadmill
    'unknown_145', 'unknown_146', 'unknown_147'
]
UNKNOWN_COLUMN_MAP = {
    'unknown_107': 'is_moving', # Boolean
    'unknown_134': 'unknown_134', # Nones
    'unknown_135': 'unknown_135', # Integer
    'unknown_136': 'wrist_heart_rate', # BPM
    'unknown_137': 'stamina_potential', # Integer 0-100
    'unknown_138': 'stamina', # Integer 0-100
    'unknown_140': 'grade_adjusted_pace', # Millimeters per second
    'unknown_143': 'body_battery', # Integer 0-100
    'unknown_145': 'unknown_145', # Integer
    'unknown_146': 'unknown_146', # Nones
    'unknown_147': 'unknown_147', # Nones
    'unknown_87': 'cycle_length', # Millimeters
    'unknown_90': 'performance_condition' # Integer
}


def get_sport(fit: FitFile) -> Union[str, str]:
    """Return the sport string from a FIT file, if present. Lowercased when returned."""
    sport = ''
    sub_sport = ''

    for msg in fit.get_messages('session'):
        fields = {f.name: f.value for f in msg}
        if fields.get('sport') is not None and sport == '':
            sport = str(fields['sport']).lower()
        if fields.get('sub_sport') is not None and sub_sport == '':
            sub_sport = str(fields['sub_sport']).lower()
        if sport != '' and sub_sport != '':
            break

    if sport == '' or sub_sport == '':
        for msg in fit.get_messages('sport'):
            fields = {f.name: f.value for f in msg}
            if sport == '' and fields.get('sport') is not None:
                sport = str(fields['sport']).lower()
            if sub_sport == '' and fields.get('sub_sport') is not None:
                sub_sport = str(fields['sub_sport']).lower()
            if sport != '' and sub_sport != '':
                break

    return sport, sub_sport


def fit_to_df(fit: FitFile) -> pd.DataFrame:
    """Read a .fit file and return a pandas DataFrame."""
    rows = []
    for record in fit.get_messages('record'):
        data = {d.name: d.value for d in record}
        rows.append(data)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=EXPECTED_FIT_COLUMNS)

    df.rename(columns=UNKNOWN_COLUMN_MAP, inplace=True)
    df['sport'], df['sub_sport'] = get_sport(fit)
    return df


def extract_event_data(df: pd.DataFrame) -> dict:
    """Extract relevant data from a DataFrame for event creation."""
    if df.empty:
        return {}

    if df['sport'].iloc[0] == 'running':
        df['sport'] = 'run'

    if df['sub_sport'].iloc[0] == 'generic':
        df['sub_sport'] = 'road'

    elapsed_seconds = tu.elapsed_seconds(df['timestamp'])
    elapsed_hours = tu.seconds_to_hours(elapsed_seconds)
    hhmmss = tu.hours_to_hhmmss(elapsed_hours)

    return {
        'start_utc': df['timestamp'].min(),
        'end_utc': df['timestamp'].max(),
        'elapsed_time': hhmmss,
        'distance': df['distance'].max(),
        'elevation_gain': df['enhanced_altitude'].diff().fillna(0).clip(lower=0).cumsum().max(),
        'sport': df['sport'].iloc[0],
        'sub_sport': df['sub_sport'].iloc[0]
    }
