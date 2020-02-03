import redis
import json


PACE_MESSAGE = 'PACING_ON'
UNPACE_MESSAGE = 'PACING_OFF'


class PacerUnpacer(object):
    def __init__(self, host="10.0.8.0", port=6379, channel='daemon_broadcast'):
        self._redis = redis.StrictRedis(host, port)
        self._channel = channel

        self.paced = False

    def pace(self):
        self.paced = True
        self._publish(PACE_MESSAGE)

    def unpace(self):
        self.paced = False
        self._publish(UNPACE_MESSAGE)

    def _publish(self, msg):
        data = {'type': msg}
        self._redis.publish(self._channel, json.dumps(data))


if __name__ == '__main__':
    a = PacerUnpacer()
    try:
        while True:
            if a.paced:
                print('Press ENTER to unpace')
                input()
                a.unpace()
                print('Sent unpace command')
            else:
                print('Press ENTER to pace')
                input()
                a.pace()
                print('Sent pace command')
    except KeyboardInterrupt:
        print("\nPacer stopped")
