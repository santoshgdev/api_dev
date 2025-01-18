"""Strava specific requests."""
import requests

from strava.entities import StravaURLs
from utils.logging_utils import logger


def get_strava_access_token(
    client_id: str, client_secret: str, refresh_token: str, grant_type: str
) -> dict:
    """Retrieve strava access token."""
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": grant_type,
    }

    response = requests.post(StravaURLs.AUTH_URL.value, data=payload)
    if response.status_code != 200:
        logger.error(f"Request to strava failed with status {response.status_code}")
    return response.json()
