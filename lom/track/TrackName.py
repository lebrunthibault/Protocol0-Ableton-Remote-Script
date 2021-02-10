import Live
from typing import TYPE_CHECKING, Optional, List

from _Framework.SubjectSlot import subject_slot_group
from _Framework.Util import clamp
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class TrackName(AbstractObject):
    __subject_events__ = ('base_name',)

    def __init__(self, track, *a, **k):
        # type: (SimpleTrack) -> None
        super(TrackName, self).__init__(*a, **k)
        self.track = track
        self.tracks = [self.track]
        self.parts = []  # type: List[str]
        self.base_name = ""
        self.playing_slot_index = 0
        self.preset_index = 0
        self._name_listener.add_subject(self.track._track)
        self._name_listener(self.track._track)

    def __repr__(self):
        return "TrackName of %s" % self.track

    @subject_slot_group("name")
    def _name_listener(self, changed_track):
        # type: (Live.Track.Track) -> None
        self.parts = changed_track.name.split(" - ")
        self.base_name = self.parts[0]
        try:
            self.playing_slot_index = int(self.parts[1])
        except (ValueError, IndexError):
            self.playing_slot_index = 0
        try:
            self.preset_index = int(self.parts[2])
        except (ValueError, IndexError):
            self.preset_index = 0

        for track in [track for track in self.tracks if track._track != changed_track]:
            if track.base_track.name != changed_track.name:
                self.parent.defer(lambda: setattr(track.base_track, "name", changed_track.name))

    def link_track(self, track):
        # type: (AbstractTrack) -> None
        self.tracks.append(track)
        self._name_listener.add_subject(track._track)

    def set(self, base_name=None, playing_slot_index=None, preset_index=None):
        # type: (Optional[str], Optional[int], Optional[int]) -> None
        playing_slot_index = playing_slot_index if playing_slot_index is not None else self.playing_slot_index
        playing_slot_index = clamp(playing_slot_index, -1, len(self.track.song.scenes) - 1)

        if base_name and base_name != self.base_name:
            # noinspection PyUnresolvedReferences
            self.notify_base_name()

        name = "%s - %s" % (base_name if base_name else self.base_name, playing_slot_index)

        if self.track.instrument:
            preset_index = preset_index if preset_index is not None else self.preset_index
            preset_index = max(0, preset_index)
            name += " - %s" % preset_index

        self.track.name = name
