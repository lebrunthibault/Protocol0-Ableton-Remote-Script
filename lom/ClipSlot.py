from typing import Any, Optional, TYPE_CHECKING

import Live
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack

from a_protocol_0.utils.log import log


class ClipSlot(AbstractObject):
    def __init__(self, clip_slot, index, track=None):
        # type: (Any, int, Optional["SimpleTrack"]) -> None
        self.clip_slot = clip_slot
        self.track = track
        self.index = index

        if self.clip_slot.is_triggered_has_listener(self.is_triggered_listener):
            self.clip_slot.remove_is_triggered_listener(self.is_triggered_listener)
        self.clip_slot.add_is_triggered_listener(self.is_triggered_listener)
        if self.clip_slot.has_clip_has_listener(self.has_clip_listener):
            self.clip_slot.remove_has_clip_listener(self.has_clip_listener)
        self.clip_slot.add_has_clip_listener(self.has_clip_listener)

    def __nonzero__(self):
        return self.clip_slot is not None

    def __eq__(self, other):
        if isinstance(other, ClipSlot):
            return self.clip_slot == other.clip_slot
        return False

    def is_triggered_listener(self):
        return
        self.parent.wait(1, lambda: setattr(self.track, "name", TrackName(self.track).get_track_name_for_clip_index(self.index)))

    def has_clip_listener(self):
        if self.has_clip and self.track.is_audio:
            self.parent.wait(10, lambda: log("delayed has clip listener"))
            # self.parent.wait(10, lambda: setattr(self.clip.clip, "warp_mode", Live.Clip.WarpMode.complex))

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
