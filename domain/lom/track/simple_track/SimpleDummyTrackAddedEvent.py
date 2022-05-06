import Live


class SimpleDummyTrackAddedEvent(object):
    def __init__(self, track):
        # type: (Live.Track.Track) -> None
        self.track = track
