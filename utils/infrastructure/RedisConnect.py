"""Redis Connection Module."""
import json
from os import environ

import redis

from utils.cloud_utils import get_secret
from utils.logging_utils import logger


class RedisConnect:
    """Infrastructure Redis Connect."""
    def __init__(self):
        """Init function."""
        pass

    def open_connection(self):
        """Open Redis connection."""
        redis_info = get_secret(environ['PROJECT_ID'], "redis_dev")
        self.interface = redis.Redis(host=redis_info["host"],
                                     port=redis_info["port"],
                                     username=redis_info["user"],
                                     password=redis_info["pw"])

    def close_connection(self):
        """Close Redis connection."""
        self.interface.close()


    def write_redis(self, key: str, value: dict, ttl: None | int=None) -> None:
        """Write key-value to redis db specified in interface.

        Args:
            key: str representing key name.
            value: dict representing value.
            ttl: int representing ttl in seconds.

        Raises:
            RedisError
        """
        self.open_connection()
        try:
            self.interface.set(name=key, value=json.dumps(value))
            if ttl:
                self.interface.expire(name=key, time=ttl)

        except redis.RedisError as exc:
            logger.error(f"Failed to set key '{key}': {exc}")
        finally:
            self.close_connection()

    def read_redis(self, key: str) -> dict | None:
        """Read from redis interface given a key.

        Args:
            key: str representing key name

        Returns:
            Either dict or None depending on if key is available

        Raises:
            RedisError
        """
        self.open_connection()
        try:
            value = self.interface.get(key)

            if value is None:
                logger.info(f"Failed to get key '{key}'; does not exist")
            else:
                return json.loads(value)

        except redis.RedisError as exc:
            logger.error(f"Failed to get key '{key}': {exc}")
            return None
        finally:
            self.close_connection()
