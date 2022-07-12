from _Framework.SubjectSlot import subject_slot
from typing import Optional, Type

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.decorators import defer


class NormalGroupTrack(AbstractGroupTrack):
    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(NormalGroupTrack, self).__init__(base_group_track=base_group_track)
        self._solo_listener.subject = base_group_track._track

    @classmethod
    def make(cls, base_group_track):
        # type: (SimpleTrack) -> NormalGroupTrack
        from protocol0.domain.lom.track.drums.DrumsTrack import DrumsTrack

        if DrumsTrack.is_track_valid(base_group_track):
            return DrumsTrack(base_group_track)
        else:
            return NormalGroupTrack(base_group_track)

    @subject_slot("solo")
    @defer
    def _solo_listener(self):
        # type: () -> None
        for sub_track in self.sub_tracks:
            sub_track.solo = self.solo

    def on_added(self):
        # type: () -> None
        super(NormalGroupTrack, self).on_added()
        self.name = self.computed_name

    @property
    def computed_name(self):
        # type: () -> str
        # tracks have all the same name
        unique_sub_track_names = list(set([sub_track.name for sub_track in self.sub_tracks]))
        if len(unique_sub_track_names) == 1:
            return unique_sub_track_names[0]

        # tracks have all the same instrument
        common_subtracks_instrument_class = self._common_subtracks_instrument_class

        if common_subtracks_instrument_class:
            return common_subtracks_instrument_class.NAME

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
    def _common_subtracks_instrument_class(self):
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
