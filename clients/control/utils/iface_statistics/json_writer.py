import json
import threading


class JsonWriter(object):
    def __init__(self, file_name):
        self._file_name = file_name
        self._file = None
        self._opened = False
        self._lock = threading.Lock()

    def open(self):
        with self._lock:
            self._file = open(self._file_name, 'w')
        self._opened = True

    def close(self):
        if self._opened:
            with self._lock:
                self._file.close()
            self._opened = False

    def write(self, data: dict):
        with self._lock:
            self._file.write("{}\n".format(json.dumps(data)))

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
