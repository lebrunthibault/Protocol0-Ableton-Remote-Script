import Live

class ClipLoopChangedEvent(object):
    def __init__(self, clip):
        # type:(Live.Clip.Clip) -> None
        self.live_clip = clip
