from typing import TYPE_CHECKING

from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.log import log

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.ClipSlot import ClipSlot


# noinspection PyTypeHints
class ClipSlotListenersMixin(object):
    def has_clip_listener(self):
        # type: ("ClipSlot") -> None
        log("clip_slot has_clip_listener")
        self.clip.name = "[] sel/name '{0}'".format(TrackName(self.track).get_track_name_for_clip_index(self.index))
