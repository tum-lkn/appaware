import json

from .abstract_logger import AbstractLogger


class ConsoleLogger(AbstractLogger):
    def __init__(self):
        pass

    def log(self, data: dict, stat_type: str):
        print(json.dumps(data, indent=4, sort_keys=True))

    def open(self):
        pass

    def close(self):
        pass
