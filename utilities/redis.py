import redis
from redis.exceptions import RedisError
from .constants import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

class RedisHelper(object):
    def __init__(self) -> None:
        pass

    def redis_connection(self, host=None):
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            db=0,
            socket_connect_timeout=60,
            socket_timeout=60,
            retry_on_timeout=True,
        )

    def redis_connection_pipeline(self):
        return self.redis_connection().pipeline()

    def add_to_redis_set(self, set_name: str, data: str):
        try:
            r = self.redis_connection()
            r.sadd(set_name, data)
            return True
        except RedisError as e:
            print(f"Redis error: {e}")
            return False
