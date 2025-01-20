"""Application entry point."""
from os import environ

import fire

from strava.request_utils import refresh_access_token_at_expiration
from utils.logging_utils import logger
from utils.task_utils import load_into_env_vars


def handler(options: dict) -> None:
    """Entry point for the application."""
    load_into_env_vars(options)
    # InfrastructureNames = DynamicEnum.from_dict(
    #     get_secret(environ["INFRASTRUCTURE_SECRET"])[environ["STAGE"]]
    # )
    logger.info("Task handler started")
    logger.info(f"Project ID: {environ['PROJECT_ID']}")
    refresh_access_token_at_expiration()
    # activity_id = get_all_data(InfrastructureNames)


if __name__ == "__main__":
    fire.Fire(handler)
