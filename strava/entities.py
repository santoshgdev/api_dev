"""Strava specific enums."""
from enum import Enum


class StravaURLs(Enum):
    """Strava specific URLs."""

    AUTH_URL = "https://www.strava.com/oauth/authorize"
    ATHLETE_URL = "https://www.strava.com/api/v3/athlete"
    ACTIVITY_URL = "https://www.strava.com/api/v3/activity"
