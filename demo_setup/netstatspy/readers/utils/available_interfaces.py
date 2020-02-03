import os


class AvailableInterfaces(object):
    @staticmethod
    def get_interfaces() -> list:
        # returns all available interfaces
        return [name for name in os.listdir('/sys/class/net') if os.path.isdir(os.path.join('/sys/class/net', name))]
