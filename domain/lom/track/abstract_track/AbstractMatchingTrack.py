from argparse import ArgumentError

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrackClips import (
    SimpleAudioTrackClips,
)
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent


class AbstractMatchingTrack(SlotManager):
    def __init__(self, base_track):
        # type: (SimpleTrack) -> None
        super(AbstractMatchingTrack, self).__init__()
        self._base_track = base_track

        self._track = None  # type: Optional[SimpleAudioTrack]
        # let tracks be mapped
        Scheduler.defer(self._init)

    def __repr__(self):
        # type: () -> str
        return "%s of %s" % (self.__class__.__name__, self._track)

    def _init(self):
        # type: () -> None
        self._track = self._get_track()

        if self._track is None:
            return

        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        # merge the file path mapping in one
        if isinstance(self._base_track, SimpleAudioTrack):
            self._base_track.file_path_mapping.update(self._track.file_path_mapping)
            self._track.file_path_mapping = self._base_track.file_path_mapping

        tracks = [self._base_track._track, self._track._track]
        self._solo_listener.replace_subjects(tracks)
        self._name_listener.replace_subjects(tracks)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackArmState) and self._track is not None:
            if observable.is_armed:
                self._connect_base_track_routing()
            else:
                self._activate_base_track()

    def _get_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        return find_if(
            lambda t: t != self._base_track
            and t.index != self._base_track.index  # when multiple objects for the same track
            and not t.is_foldable
            and t.name == self._base_track.name,
            Song.simple_tracks(SimpleAudioTrack),
        )

    def _assert_valid_track_name(self):
        # type: () -> None
        excluded_names = [d.value.lower() for d in DeviceEnum if d.is_instrument]
        excluded_names += ["synth", "bass"]

        assert self._base_track.name.lower() not in excluded_names, "Track name should be specific"

    def connect_base_track(self):
        # type: () -> Optional[Sequence]
        # plug the matching track in its main audio track
        if self._track is None:
            return None

        self._base_track.color = self._track.color
        self._connect_base_track_routing()
        return None

    def _connect_base_track_routing(self):
        # type: () -> None
        self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._track.input_routing.type = InputRoutingTypeEnum.NO_INPUT  # type: ignore
        self._base_track.output_routing.track = self._track  # type: ignore

    def _activate_base_track(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        try:
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        except ArgumentError:
            pass

    @subject_slot_group("solo")
    @defer
    def _solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        self._base_track.solo = track.solo
        if self._track is not None:
            self._track.solo = track.solo

    @subject_slot_group("name")
    @defer
    def _name_listener(self, _):
        # type: (Live.Track.Track) -> None
        """on any name change, cut the link"""
        self.disconnect()

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        raise NotImplementedError

    def broadcast_clips(self, clip_infos, source_track = None):
        # type: (SimpleAudioTrackClips, SimpleAudioTrack) -> Optional[Sequence]
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        source_track = source_track or self._base_track
        assert isinstance(source_track, SimpleAudioTrack), "can only broadcast audio clips"
        if self._track is None:
            return None

        return clip_infos.broadcast_to_track(source_track, self._track)

    @defer
    def disconnect(self):
        # type: () -> None
        super(AbstractMatchingTrack, self).disconnect()
        if (
            self._track is None
            or not liveobj_valid(self._track._track)
            or not liveobj_valid(self._base_track._track)
        ):
            return

        if len([t for t in Song.simple_tracks() if t.output_routing.track == self._track]) == 0:  # type: ignore
            self._activate_base_track()
