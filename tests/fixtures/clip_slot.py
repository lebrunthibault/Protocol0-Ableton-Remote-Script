from _Framework.SubjectSlot import subject_add_event, Subject


class AbletonClipSlot(Subject):
    __subject_events__ = ("has_clip",)

    def __init__(self, clip=None):
        self.clip = clip
        self.has_clip = bool(clip)

# subject_add_event(AbletonClipSlot, "has_clip")
