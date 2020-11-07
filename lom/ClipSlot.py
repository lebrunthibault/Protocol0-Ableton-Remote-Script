from typing import Any, Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.Clip import Clip

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


class ClipSlot(object):
    def __init__(self, clip_slot, index, track=None):
        # type: (Any, int, Optional["SimpleTrack"]) -> None
        self.clip_slot = clip_slot
        self.track = track
        self.index = index

    def __nonzero__(self):
        return self.clip_slot is not None

    def __eq__(self, other):
        if isinstance(other, ClipSlot):
            return self.clip_slot == other.clip_slot
        return False

    @property
    def is_triggered(self):
        # type: () -> bool
        return self.clip_slot.is_triggered

    @property
    def has_clip(self):
        # type: () -> bool
        return self.clip_slot.has_clip

    @property
    def clip(self):
        # type: () -> Optional[Clip]
        return Clip(self.clip_slot, self.index, self.track) if self.has_clip else None

    def fire(self, record_length):
        # type: (int) -> None
        self.clip_slot.fire(record_length=record_length)
