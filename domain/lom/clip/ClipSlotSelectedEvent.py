import Live


class ClipSlotSelectedEvent(object):
    def __init__(self, live_clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        self.live_clip_slot = live_clip_slot
