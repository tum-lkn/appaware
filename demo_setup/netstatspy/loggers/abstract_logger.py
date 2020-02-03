class AbstractLogger(object):
    def log(self, data: dict, stat_type: str):
        raise NotImplementedError

    def log_multiple(self, data: list, stat_type: str):
        for stat in data:
            self.log(stat, stat_type)

    def open(self):
        # open a file, network connection, ..., to write the data.
        raise NotImplementedError

    def close(self):
        # close the file, network connection, ...
        raise NotImplementedError
