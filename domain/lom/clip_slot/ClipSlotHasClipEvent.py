import Live

class ClipSlotHasClipEvent(object):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        self.live_track = live_track
