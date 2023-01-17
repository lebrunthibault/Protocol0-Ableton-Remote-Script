from _Framework.SubjectSlot import subject_slot
from typing import Optional, Type

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.timing import defer


class NormalGroupTrack(AbstractGroupTrack):
    @classmethod
    def make(cls, base_group_track):
        # type: (SimpleTrack) -> NormalGroupTrack
        from protocol0.domain.lom.track.group_track.DrumsTrack import DrumsTrack
        from protocol0.domain.lom.track.simple_track.audio.special.ReferenceTrack import ReferenceTrack
        from protocol0.domain.lom.track.group_track.VocalsTrack import VocalsTrack

        if DrumsTrack.is_track_valid(base_group_track):
            return DrumsTrack(base_group_track)
        elif base_group_track.name == ReferenceTrack.TRACK_NAME:
            return ReferenceTrack(base_group_track)
        elif VocalsTrack.TRACK_NAME == base_group_track.name.strip():
            return VocalsTrack(base_group_track)
        else:
            return NormalGroupTrack(base_group_track)

    def on_added(self):
        # type: () -> None
        super(NormalGroupTrack, self).on_added()
        self.name = self.computed_name
        if len(set(t.color for t in self.sub_tracks)) == 1:
            self.color = self.sub_tracks[0].color

    @subject_slot("solo")
    @defer
    def _solo_listener(self):
        # type: () -> None
        if self.solo:
            for sub_track in self.sub_tracks:
                sub_track.solo = True

    @property
    def computed_name(self):
        # type: () -> str
        # tracks have all the same name
        base_name = self._computed_base_name
        if base_name != self.name:
            return "%s Group" % base_name
        else:
            return self.name

    @property
    def _computed_base_name(self):
        # type: () -> str
        unique_sub_track_names = list(set([sub_track.name for sub_track in self.sub_tracks]))
        if len(unique_sub_track_names) == 1:
            return unique_sub_track_names[0]

        # tracks have all the same instrument
        common_sub_tracks_instrument_class = self._common_sub_tracks_instrument_class

        if common_sub_tracks_instrument_class:
            return common_sub_tracks_instrument_class.NAME

        def _name_prefix(track):
            # type: (AbstractTrack) -> str
            return track.base_track.name.split(" ")[0]

        # checking if all sub tracks have the same prefix
        unique_sub_tracks_name_prefixes = list(
            set([_name_prefix(sub_track) for sub_track in self.sub_tracks])
        )
        if len(unique_sub_tracks_name_prefixes) == 1 and unique_sub_tracks_name_prefixes[0]:
            return unique_sub_tracks_name_prefixes[0]

        return self.name

    @property
    def _common_sub_tracks_instrument_class(self):
        # type: () -> Optional[Type[InstrumentInterface]]
        sub_tracks_instrument_classes = [
            sub_track.instrument.__class__ for sub_track in self.sub_tracks if sub_track.instrument
        ]

        unique_sub_tracks_instrument_classes = list(set(sub_tracks_instrument_classes))
        if (
            len(sub_tracks_instrument_classes) == len(self.sub_tracks)
            and len(unique_sub_tracks_instrument_classes) == 1
        ):
            return unique_sub_tracks_instrument_classes[0]
        else:
            return None
