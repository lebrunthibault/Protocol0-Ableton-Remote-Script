import pytest

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack

class AbletonTrack:
    def __init__(self):
        self.name = "kicks - 0"

@pytest.fixture
def simple_track():
    return SimpleTrack(AbletonTrack())