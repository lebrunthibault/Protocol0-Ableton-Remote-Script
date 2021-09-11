import re

from typing import TYPE_CHECKING, Optional, Any, List

import Live
from _Framework.SubjectSlot import subject_slot_group
from protocol0.config import Config
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.lom.AbstractObjectName import AbstractObjectName
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


class AbstractTrackName(AbstractObjectName):
    def __init__(self, track, *a, **k):
        # type: (AbstractTrack, Any, Any) -> None
        super(AbstractTrackName, self).__init__(*a, **k)
        self.track = track
        self.selected_preset_index = None  # type: Optional[int]
        self._instrument_listener.subject = self.track
        self._name_listener.add_subject(self.track._track)
        self._name_listener(self.track._track)

    @property
    def instrument_names(self):
        # type: () -> List[str]
        return [_class.NAME.lower() for _class in AbstractInstrument.INSTRUMENT_CLASSES if _class.NAME]

    @p0_subject_slot("instrument")
    def _instrument_listener(self):
        # type: () -> None
        self._selected_preset_listener.subject = self.track.instrument

    @p0_subject_slot("selected_preset")
    def _selected_preset_listener(self):
        # type: () -> None
        """ Called once at track instantiation time """
        # abstract_group_tracks handle display
        if self.track.abstract_group_track:
            return

        if self.track.instrument.selected_preset:
            self.selected_preset_index = self.track.instrument.selected_preset.index

        if self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME:
            if self.track.instrument.selected_preset:
                self.base_name = self.track.instrument.selected_preset.name

        self.update()

    @subject_slot_group("name")
    def _name_listener(self, _):
        # type: (Live.Track.Track) -> None
        match = re.match(
            "^(((\d+)|#)[\s-]*)?(?P<base_name>[^()]*)[()]*(\((?P<selected_preset_index>\d+)\))?$", self.track.name
        )
        # _ is a reserved character for track names
        self.base_name = match.group("base_name").strip().replace("_", " ") if match else ""

        if Config.FIX_OUTDATED_SETS:
            self.base_name = self.base_name.split("-")[0].strip()

        if match and match.group("selected_preset_index"):
            self.selected_preset_index = int(match.group("selected_preset_index")) - 1

    @property
    def _should_recompute_base_name(self):
        # type: () -> bool
        return (
                not self.base_name
                or self.base_name.lower() == self.track.DEFAULT_NAME.lower()
                or (
                        self.track.instrument
                        and not self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME
                )
                or self.base_name.lower() in self.instrument_names
        )

    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        self.base_name = base_name or self.base_name

        if self._should_recompute_base_name:
            self.base_name = str(self.track.computed_base_name)

        name = self.base_name
        if not self.track.abstract_group_track and name[0:1].islower():
            name = name.title()

        # displaying only on group track when track is part of an AbstractGroupTrack
        if self.track.instrument and self.selected_preset_index is not None and self.track.abstract_group_track is None:
            if self.track.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.INDEX:
                name += " (%d)" % (self.selected_preset_index + 1)

        from protocol0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack

        if isinstance(self.track, SimpleGroupTrack):
            name += " (%d)" % len(self.track.sub_tracks)

        self.track.name = name

        # propagating upwards
        if self.track.group_track and not self.track.abstract_group_track:
            self.track.group_track.track_name.update()
