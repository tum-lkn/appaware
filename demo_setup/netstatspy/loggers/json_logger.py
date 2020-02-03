import json

from .abstract_logger import AbstractLogger


class JsonLogger(AbstractLogger):
    def __init__(self, filename):
        self._filename = filename
        self._file = None
        self._opened = False

    def open(self):
        if self._opened:
            return
        self._file = open(self._filename, 'w')
        self._opened = True

    def close(self):
        if not self._opened:
            return
        self._file.close()

    def log(self, data: dict, stat_type: str):
        self._file.write(json.dumps({'type': stat_type, 'data': data}))
        self._file.write('\n')
