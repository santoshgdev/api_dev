"""Application entry point."""
from os import environ

from strava.request_utils import get_all_activities, refresh_access_token_at_expiration
from utils.logging_utils import logger


def handler() -> None:
    """Entry point for the application."""
    logger.info("Task handler started")
    logger.info(f"Project ID: {environ['PROJECT_ID']}")
    refresh_access_token_at_expiration()
    get_all_activities()


if __name__ == "__main__":
    handler()
