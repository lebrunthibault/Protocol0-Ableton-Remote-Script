from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackListenerMixin(object):
    def init_listeners(self):
        # type: ("SimpleTrack") -> None
        if self.track.playing_slot_index_has_listener(self.playing_slot_index_listener):
            self.track.remove_playing_slot_index_listener(self.playing_slot_index_listener)
        self.track.add_playing_slot_index_listener(self.playing_slot_index_listener)

    def playing_slot_index_listener(self, execute_later=True):
        # type: ("SimpleTrack", bool) -> None
        if execute_later:
            return self.parent.wait(1, partial(self.playing_slot_index_listener, execute_later=False))
        self.build_clip_slots()
        self.refresh_name()
