import re
from functools import partial
from typing import TYPE_CHECKING, Optional

import Live

from _Framework.SubjectSlot import subject_slot_group
from _Framework.Util import clamp
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

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
        self.base_name = ""
        self.selected_preset_index = 0

        self._instrument_listener.subject = self.track
        self._name_listener.add_subject(self.track._track)
        self._name_listener(self.track._track)

    def __repr__(self):
        return "TrackName of %s" % self.track

    @p0_subject_slot("instrument")
    def _instrument_listener(self):
        self._selected_preset_listener.subject = self.track.instrument

    @p0_subject_slot("selected_preset")
    def _selected_preset_listener(self):
        setter = partial(self.set_track_name, selected_preset_index=self.track.instrument.selected_preset.index)
        if self.track.instrument.should_display_selected_preset_name:
            setter(base_name=self.track.instrument.selected_preset.name)
        else:
            setter()

    @subject_slot_group("name")
    def _name_listener(self, changed_track):
        # type: (Live.Track.Track) -> None
        match = re.match("^(?P<base_name>[^()]*).*\((?P<selected_preset_index>\d+)\)\s*$", self.track.name)

        previous_base_name = self.base_name
        # _ is a reserved character for track names
        self.base_name = match.group("base_name").strip().replace("_", " ") if match else ""
        self.selected_preset_index = int(match.group("selected_preset_index") or 0) if match else 0

        for track in [track for track in self.tracks if track._track != changed_track]:
            if track.base_track.name != changed_track.name:
                self.parent.defer(lambda: setattr(track.base_track, "name", changed_track.name))

        if self.base_name and self.base_name != previous_base_name:
            # noinspection PyUnresolvedReferences
            self.notify_base_name()

    def link_track(self, track):
        # type: (AbstractTrack) -> None
        self.tracks.append(track)
        self._name_listener.add_subject(track._track)

    def set_track_name(self, base_name=None, playing_slot_index=None, selected_preset_index=None):
        # type: (Optional[str], Optional[int], Optional[int]) -> None
        previous_base_name = self.base_name
        self.base_name = base_name if base_name else self.base_name

        selected_preset_index = selected_preset_index if selected_preset_index is not None else self.selected_preset_index
        self.selected_preset_index = max(0, selected_preset_index)

        name = self.base_name
        if self.track.instrument and self.track.instrument.SHOULD_DISPLAY_SELECTED_PRESET_INDEX:
            name += " (%s)" % self.selected_preset_index

        if self.base_name and self.base_name != previous_base_name:
            # noinspection PyUnresolvedReferences
            self.notify_base_name()
        seq = Sequence(silent=True)
        seq.add(partial(setattr, self.track, "name", name), wait=1)  # wait is necessary
        return seq.done()
