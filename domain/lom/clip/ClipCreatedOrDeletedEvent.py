import Live


class ClipCreatedOrDeletedEvent(object):
    def __init__(self, live_clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        self.live_clip_slot = live_clip_slot

    def target(self):
        # type: () -> object
        return self.live_clip_slot
