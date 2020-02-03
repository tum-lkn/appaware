class StatsReader(object):
    @classmethod
    def get_stats_with_type_dict(cls, interface_name: str) -> dict:
        stats = cls.get_stats(interface_name)
        return {'type':  cls.get_type(),
                'stats': stats}

    @staticmethod
    def get_stats(interface_name: str) -> list:
        raise NotImplementedError

    @staticmethod
    def get_type() -> str:
        raise NotImplementedError
