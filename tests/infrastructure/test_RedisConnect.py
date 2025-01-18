import json
from os import environ
from unittest.mock import patch

from utils.infrastructure.RedisConnect import RedisConnect


class TestRedisConnect:
    """Test module for RedisConnect."""

    @patch("utils.infrastructure.RedisConnect.get_secret")
    @patch("redis.Redis")
    @patch.dict(environ, {"PROJECT_ID": "1234"})
    def test_write_redis(self, mock_redis, mock_get_secret):
        """Test for writing to Redis."""
        mock_get_secret.return_value = {
            "host": "value1",
            "port": "value2",
            "user": "value3",
            "pw": "value4",
        }

        redis_instance = mock_redis.return_value
        redis_connect = RedisConnect()
        key = "redis_test_key"
        value = {"redis_key": "redis_value"}
        ttl = 60

        redis_connect.write_redis(key, value, ttl)

        redis_instance.setex.assert_called_with(
            name=key, value=json.dumps(value), time=ttl
        )

    @patch("utils.cloud_utils.get_secret")
    @patch("redis.Redis")
    @patch.dict("os.environ", {"PROJECT_ID": "1234"})
    def test_read_redis(self, mock_redis, mock_get_secret):
        """Test for reading from Redis."""
        mock_get_secret.return_value = {
            "host": "value1",
            "port": "value2",
            "user": "value3",
            "pw": "value4",
        }

        redis_instance = mock_redis.return_value
        key = "test_key"
        expected_value = {"key": "value"}
        redis_instance.get.return_value = json.dumps(expected_value)
        redis_connect = RedisConnect()
        result = redis_connect.read_redis(key)

        assert result == expected_value
        redis_instance.get.assert_called_once_with(key)

    @patch("utils.infrastructure.RedisConnect.get_secret")
    @patch("redis.Redis")
    @patch.dict("os.environ", {"PROJECT_ID": "1234"})
    def test_read_redis_key_not_exist(self, mock_redis, mock_get_secret):
        """Test for reading from Redis assuming the key doesn't exist."""
        mock_get_secret.return_value = {
            "host": "value1",
            "port": "value2",
            "user": "value3",
            "pw": "value4",
        }

        redis_instance = mock_redis.return_value
        key = "non_existent_key"
        redis_instance.get.return_value = None

        redis_connect = RedisConnect()
        result = redis_connect.read_redis(key)

        assert result is None
        redis_instance.get.assert_called_once_with(key)
