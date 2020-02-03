import redis
import json
import logging

from .abstract_logger import AbstractLogger


log = logging.getLogger(__name__)


class RedisPusher(AbstractLogger):
    def __init__(self, redis_ip: str, redis_port: int):
        self._redis = None
        self._ip = redis_ip
        self._port = redis_port

    def open(self):
        log.debug("Opening redis connection")
        self._redis = redis.StrictRedis(host=self._ip, port=self._port, db=0)

    def close(self):
        log.debug("Closing redis connection")
        self._redis.connection_pool.disconnect()

    def log(self, data: dict, stat_type: str):
        log.debug("Publishing stats to channel '{}'".format(channel))
        self._redis.publish(stat_type, json.dumps(data))
