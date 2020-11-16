from functools import partial
from typing import TYPE_CHECKING

from a_protocol_0.utils.log import log

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackListenersMixin(object):
    def name_listener(self):
        # type: ("SimpleTrack") -> None
        if self.song.await_track_rename and self.name != self.original_name:
            log("deferring track set name call")
            self.song.await_track_rename = False
            self.song.parent.wait(1, partial(setattr, self, "name", self.original_name))
