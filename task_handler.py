"""Application entry point."""
from os import environ

from utils.cloud_utils import get_secret
from utils.logging_utils import logger


def handler():
    """Entry point for the application."""
    logger.info("Task handler started")

    project_id = environ["PROJECT_ID"]
    logger.info(f"Project ID: {project_id}")

    get_secret(project_id, "strava_api")


if __name__ == "__main__":
    handler()
