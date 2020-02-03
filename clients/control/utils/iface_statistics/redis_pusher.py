import redis
import threading
import json
import logging


log = logging.getLogger(__name__)


class RedisPusher(threading.Thread):
    def __init__(self, redis_ip: str, redis_port: int):
        threading.Thread.__init__(self)
        log.info("Setting up Redis pusher")
        self._redis = redis.StrictRedis(host=redis_ip, port=redis_port, db=0)

    def publish(self, data: dict, channel: str):
        log.debug("Publishing stats to channel 'statistics.{}'".format(channel))
        self._redis.publish('statistics.{}'.format(channel), json.dumps(data))
