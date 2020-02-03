import redis
import threading
import logging
import queue
import sys


REDIS_MESSAGE_TYPE = 'redis'


class RedisCommunicator(threading.Thread):
    def __init__(self, host: str, port: int, channels, comm_queue: queue.Queue, db):
        threading.Thread.__init__(self)

        # logger
        self._logger = logging.getLogger("Redis Communicator")
        self._logger.debug("Init Redis communicator")

        # state variables
        self._connected = False
        self._running = False

        # redis
        self._redis = None
        self._redis_sub = None

        self._host = host
        self._port = port
        self._channels = channels
        self._db = db
        self._comm_queue = comm_queue

    def connect(self):
        self._logger.debug("Trying to connect to redis on ip {}, port {} and channels {}".format(self._host, self._port,
                                                                                                 self._channels))
        try:
            self._redis = redis.StrictRedis(host=self._host, port=self._port, db=self._db, charset="utf-8",
                                            decode_responses=True)
            self._redis_sub = self._redis.pubsub(ignore_subscribe_messages=True)
            self._redis_sub.subscribe(self._channels)
        except redis.exceptions.ConnectionError:
            self._logger.error("Couldn't connect to redis server (%s:%s) - exiting"
                               % (self._host, self._port))
            sys.exit(-1)
        self._logger.debug("Connected to redis")
        self._connected = True

    def run(self):
        if not self._connected:
            self.connect()
        self._logger.debug("RedisCommunicator.run()")
        self._running = True

        while self._running:
            msg = self._redis_sub.get_message(timeout=0.5)
            if msg:
                self._logger.debug("received msg: \"%s\"" % msg)
                self._comm_queue.put({'type': REDIS_MESSAGE_TYPE,
                                      'data': msg})

    def stop(self):
        self._logger.debug("Stopping redis communicator")
        self._redis_sub.unsubscribe()
        self._redis_sub.close()
        self._connected = False
        self._running = False

    def publish(self, msg, channel):
        self._logger.debug("Publishing message {} on channel {}".format(msg, channel))
        self._redis.publish(channel, msg)
