"""Strava specific enums."""
from enum import Enum


class StravaURLs(Enum):
    """Strava specific URLs."""

    AUTH_URL = "https://www.strava.com/api/v3/oauth/token"
    ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
    ACTIVITY_URL = "https://www.strava.com/api/v3/activity"


class StravaKeys(Enum):
    """Strava specific keys."""

    STRAVA_ACCESS_TOKEN = "strava_access_token"
