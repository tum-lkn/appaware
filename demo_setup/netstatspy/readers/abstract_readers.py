class StatsReader(object):
    @classmethod
    def get_stats_with_type_dict(cls) -> dict:
        stats = cls.get_all_stats()
        return {'type':  cls.get_type(),
                'stats': stats}

    @classmethod
    def get_all_stats(cls) -> list:
        raise NotImplementedError

    @staticmethod
    def get_type() -> str:
        raise NotImplementedError


class TcIpQueueLimitsStatsReader(StatsReader):
    @classmethod
    def get_all_stats(cls) -> list:
        raise NotImplementedError

    @classmethod
    def get_interface_stats(cls, interface_name: str) -> dict:
        raise NotImplementedError

    @staticmethod
    def get_type() -> str:
        raise NotImplementedError
