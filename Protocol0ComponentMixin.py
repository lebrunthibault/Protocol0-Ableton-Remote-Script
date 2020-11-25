from __future__ import with_statement

from typing import TYPE_CHECKING

from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class Protocol0ComponentMixin(object):
    def __init__(self, *a, **k):
        self.parent = k["parent"]  # type: "Protocol0Component"

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.parent.current_track

    def my_song(self):
        # type: () -> Song
        return self.parent.my_song()

    def log_message(self, message):
        # type: (str) -> None
        return self.parent.log_message(message)

    def show_message(self, message):
        # type: (str) -> None
        return self.parent.show_message(message)
