"""Strava specific requests."""
from os import environ

import requests

from strava.entities import StravaKeys, StravaURLs
from utils.cloud_utils import get_secret
from utils.infrastructure.RedisConnect import RedisConnect
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


def refresh_access_token_at_expiration():
    """Refreshes strava access token if it happens to be expired."""
    redis = RedisConnect()
    if not redis.get_ttl(StravaKeys.STRAVA_ACCESS_TOKEN.value):
        logger.info("Refreshing strava access token")
        strava_secret_token = get_secret(environ["PROJECT_ID"], "strava_api")
        strava_access_token = get_strava_access_token(
            client_id=strava_secret_token["client_id"],
            client_secret=strava_secret_token["client_secret"],
            refresh_token=strava_secret_token["refresh_token"],
            grant_type=strava_secret_token["grant_type"],
        )
        redis = RedisConnect()
        redis.write_redis(
            key=StravaKeys.STRAVA_ACCESS_TOKEN.value,
            value=strava_access_token,
            ttl=strava_access_token["expires_in"] - 60,
        )
        logger.info("Refreshed strava access token")
    else:
        logger.info("Strava token still valid")
