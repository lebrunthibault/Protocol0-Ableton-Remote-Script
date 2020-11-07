from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.ClipSlot import ClipSlot


# noinspection PyTypeHints
class ClipSlotListenersMixin(object):
    def has_clip_listener(self):
        # type: ("ClipSlot") -> None
        log_ableton("clip_slot has_clip_listener")
        self.clip.name = "[] sel/name '{0}'".format(TrackName(self.track).get_track_name_for_clip_index(self.index))
