import pytest

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.device import AbletonDevice


class AbletonTrack:
    def __init__(self, devices):
        # type: (list[AbletonDevice]) -> None
        self.name = "kicks - 0"
        self.devices = devices

    def __eq__(self, other):
        if isinstance(other, AbletonTrack):
            return self.name == other.name
        return False


def simpler_track(song, index=1):
    # type: (Song, int) -> SimpleTrack
    return SimpleTrack(song, AbletonTrack(), index)