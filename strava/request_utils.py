"""Strava specific requests."""
# mypy: disable-error-code="attr-defined"
from enum import Enum
from os import environ

import requests
from cloudpathlib import GSPath

from strava.entities import StravaKeys, StravaURLs
from utils.cloud_utils import get_secret, write_json_to_storage
from utils.infrastructure.RedisConnect import RedisConnect
from utils.logging_utils import logger


def get_strava_access_token(
    client_id: str,
    client_secret: str,
    code: str,
    grant_type: str = "authorization_code",
) -> dict:
    """Retrieve strava access token."""
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": grant_type,
    }
    response = requests.post(StravaURLs.AUTH_URL.value, data=payload)
    if response.status_code != 200:
        logger.error(f"Request to strava failed with status {response.status_code}")
    return response.json()


def refresh_access_token_at_expiration():
    """Refreshes strava access token if it happens to be expired."""
    redis = RedisConnect()
    redis_ttl = redis.get_ttl(StravaKeys.STRAVA_ACCESS_TOKEN.value)
    if redis_ttl is None or redis_ttl < 0:
        write_refreshed_access_token_to_redis()
    else:
        logger.info("Strava token still valid")


def write_refreshed_access_token_to_redis():
    """Writes retrieved strava access token to redis."""
    logger.info("Refreshing strava access token")
    strava_secret_token = get_secret(environ["STRAVA_SECRET"])
    strava_access_token = get_strava_access_token(
        client_id=strava_secret_token["client_id"],
        client_secret=strava_secret_token["client_secret"],
        code=environ["AUTHORIZATION_TOKEN"],
        grant_type=strava_secret_token["grant_type"],
    )
    redis = RedisConnect()
    redis.write_redis(
        key=StravaKeys.STRAVA_ACCESS_TOKEN.value,
        value=strava_access_token,
        ttl=strava_access_token["expires_in"] - 60,
    )
    logger.info("Refreshed strava access token")


def get_all_activities(InfrastructureNames: Enum) -> None:
    """Get all activities."""
    redis = RedisConnect()
    strava_access_dict_from_redis = redis.read_redis(
        StravaKeys.STRAVA_ACCESS_TOKEN.value
    )
    strava_access_token = (
        strava_access_dict_from_redis["access_token"]
        if strava_access_dict_from_redis
        else None
    )
    if not strava_access_token:
        return None
    headers = {"Authorization": f"Bearer {strava_access_token}"}

    page_num = 1
    flag = True
    logger.debug("Getting all activities")
    while flag:
        param = {"per_page": 200, "page": page_num}
        response = requests.get(
            StravaURLs.ACTIVITY_URL.value, headers=headers, params=param
        )
        response_json = response.json()
        for activity in response_json:
            athlete_id = activity["athlete"]["id"]
            activity_id = activity["id"]
            path = GSPath(
                f"gs://{InfrastructureNames.bronze_bucket.value}/strava/athlete_id={athlete_id}/activity_id={activity_id}.json"
            )
            write_json_to_storage(path, activity)
