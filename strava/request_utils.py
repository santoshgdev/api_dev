"""Strava specific requests."""
import json

# mypy: disable-error-code="attr-defined"
from enum import Enum
from os import environ

import requests
from stravalib import Client
from stravalib.model import Stream
from tqdm import tqdm

from strava.cloud_utils import get_strava_storage_path
from strava.entities import StravaKeys, StravaModels, StravaStreams, StravaURLs
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
        raise Exception(
            f"Request to strava failed with status {response.status_code}: {response.text}"
        )
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


def get_all_data(InfrastructureNames: Enum) -> None:
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
    client = Client(access_token=strava_access_token)
    activities = list(client.get_activities())
    for activity in tqdm(activities, desc="Getting activities"):
        activity_dump = activity.model_dump()
        athlete_id, activity_id = activity_dump["athlete"]["id"], activity_dump["id"]
        path = get_strava_storage_path(
            bucket=InfrastructureNames.bronze_bucket,
            athlete_id=athlete_id,
            strava_model=StravaModels.ACTIVITY,
            activity_id=activity_id,
        )
        write_json_to_storage(path, json.loads(activity.model_dump_json()))

        streams = client.get_activity_streams(
            activity_id=activity_id, types=[e.value for e in StravaStreams]
        )
        stream_time = streams.get(StravaStreams.TIME.value, Stream()).data
        for stream in StravaStreams:
            stream_type = stream.value
            stream_data = streams.get(stream_type, Stream()).data
            if stream != StravaStreams.TIME and stream_data is not None:
                paired_streams = [
                    {"time": t, stream_type: d}
                    for t, d in zip(stream_time, stream_data)
                ]
                path = get_strava_storage_path(
                    bucket=InfrastructureNames.bronze_bucket,
                    athlete_id=athlete_id,
                    strava_model=stream,
                    activity_id=activity_id,
                )
                write_json_to_storage(path, paired_streams)
