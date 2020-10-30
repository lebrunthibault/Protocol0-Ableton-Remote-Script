import pytest

class AbletonDevice:

    def __init__(self, class_name, name = ""):
        self.class_name = class_name
        self.name = name

@pytest.fixture
def device_simpler():
    return AbletonDevice("OriginalSimpler")