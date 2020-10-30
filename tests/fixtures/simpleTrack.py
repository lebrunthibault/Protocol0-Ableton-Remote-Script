from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.device import AbletonDevice, make_device_simpler


class AbletonTrack:
    def __init__(self, device):
        # type: (AbletonDevice) -> None
        self.name = "kicks - 0"
        self.devices = [device]
        self.is_visible = True

    def __eq__(self, other):
        if isinstance(other, AbletonTrack):
            return self.name == other.name
        return False


def make_simpler_track(song, index=1):
    # type: (Song, int) -> SimpleTrack
    return SimpleTrack(song, AbletonTrack(make_device_simpler()), index)