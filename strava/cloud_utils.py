"""Cloud utils specific for Strava API."""
from enum import Enum

from cloudpathlib import GSPath

from strava.entities import StravaModels, StravaStreams


def get_strava_storage_path(
    bucket: Enum,
    athlete_id: str,
    strava_model: StravaModels | StravaStreams | None,
    **kwargs,
) -> GSPath:
    """Returns a GSPath representing a Strava storage path.

    Args:
        bucket_name: Bucket names reported as an Infrastructure Enum.
        athlete_id: Athlete ID
        strava_model: Specific Strava Model (Activity or other) or specific Strava Stream (heartrate, cadence, etc)
        **kwargs: Extra parameters, e.g. activity_id, used to build path

    Returns:
        GSPath object
    """
    path = f"gs://{bucket.value}/strava/athlete_id={athlete_id}/"
    file_name = f"activity_id={kwargs['activity_id']}.json"

    if strava_model == StravaModels.ACTIVITY:
        path += f"activity/{file_name if 'activity_id' in kwargs else ''}"

    if isinstance(strava_model, StravaStreams):
        path += f"{strava_model.value}/{file_name if 'activity_id' in kwargs else ''}"
    return GSPath(path)
