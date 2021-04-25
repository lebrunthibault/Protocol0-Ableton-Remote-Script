import re
from functools import partial

import Live
from typing import TYPE_CHECKING, Optional, Any

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class TrackName(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (AbstractTrack, Any, Any) -> None
        super(TrackName, self).__init__(*a, **k)
        self.track = track
        self.base_name = ""
        self.selected_preset_index = 0
        self._instrument_listener.subject = self.track
        self._name_listener.add_subject(self.track._track)
        self._name_listener(self.track._track)

    @p0_subject_slot("instrument")
    def _instrument_listener(self):
        # type: () -> None
        self._selected_preset_listener.subject = self.track.instrument

    @p0_subject_slot("selected_preset")
    def _selected_preset_listener(self):
        # type: () -> None
        if self.track.instrument.should_display_selected_preset_name:
            self.update(base_name=self.track.instrument.selected_preset.name)
        elif self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.INDEX:
            self.update(selected_preset_index=self.track.instrument.selected_preset.index)

    @subject_slot_group("name")
    def _name_listener(self, _):
        # type: (Live.Track.Track) -> None
        match = re.match("^(?P<base_name>[^()]*)[()]*(\((?P<selected_preset_index>\d+)\))?$", self.track.name)
        # _ is a reserved character for track names
        self.base_name = match.group("base_name").strip().replace("_", " ") if match else ""
        if self.song.fix_outdated_sets:
            self.base_name = self.base_name.split("-")[0].strip()
        if match and match.group("selected_preset_index"):
            self.selected_preset_index = int(match.group("selected_preset_index")) - 1

    def update(self, base_name=None, playing_slot_index=None, selected_preset_index=None):
        # type: (Optional[str], Optional[int], Optional[int]) -> Optional[Sequence]
        self.base_name = base_name if base_name else self.base_name

        selected_preset_index = (
            selected_preset_index if selected_preset_index is not None else self.selected_preset_index
        )
        self.selected_preset_index = max(0, selected_preset_index)

        if self.track.instrument:
            self.parent.log_dev(self.track.instrument.PRESET_DISPLAY_OPTION)
            self.parent.log_dev(self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.INDEX)
        name = self.base_name
        if (
            # self.track.abstract_track == self.track
            self.track.instrument
            and self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.INDEX
        ):
            name += " (%s)" % (self.selected_preset_index + 1)

        seq = Sequence(silent=True)
        seq.add(wait=1)
        seq.add(partial(setattr, self.track, "name", name), complete_on=lambda: self.track.name == name)
        return seq.done()
