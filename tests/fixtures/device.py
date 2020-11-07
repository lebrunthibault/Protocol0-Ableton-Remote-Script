class AbletonDevice(object):

    def __init__(self, class_name, name=""):
        self.class_name = class_name
        self.name = name


def make_device_simpler():
    return AbletonDevice("OriginalSimpler")
