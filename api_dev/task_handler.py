"""Application entry point."""
from os import environ

import fire
from fitnessllm_dataplatform.utils.cloud_utils import get_secret
from fitnessllm_dataplatform.utils.task_utils import load_into_env_vars

from api_dev.entities.enums import DynamicEnum
from api_dev.strava.request_utils import (
    get_all_data,
    refresh_access_token_at_expiration,
)
from api_dev.utils.logging_utils import logger


def handler(options: dict) -> None:
    """Entry point for the application."""
    load_into_env_vars(options)
    InfrastructureNames = DynamicEnum.from_dict(
        get_secret(environ["INFRASTRUCTURE_SECRET"])[environ["STAGE"]]
    )
    logger.info("Task handler started")
    logger.info(f"Project ID: {environ['PROJECT_ID']}")
    refresh_access_token_at_expiration()
    activity_id = get_all_data(InfrastructureNames)
    print(activity_id)


if __name__ == "__main__":
    fire.Fire(handler)
