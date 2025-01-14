"""Strava specific requests."""
import requests

from strava.entities import StravaURLs


def get_access_token(
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
    new_token = response.json()

    return new_token
