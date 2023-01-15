from argparse import ArgumentError

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
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

        tracks = [self._base_track._track, self._track._track]
        self._solo_listener.replace_subjects(tracks)
        self._name_listener.replace_subjects(tracks)

    @property
    def exists(self):
        # type: () -> bool
        return self._track is not None

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackArmState) and self._track is not None:
            if observable.is_armed:
                self.connect_base_track_routing()
            else:
                self._activate_base_track()

    @classmethod
    def get_matching_track(cls, base_track):
        # type: (AbstractTrack) -> Optional[SimpleAudioTrack]
        from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack

        return find_if(
            lambda t: t != base_track
            and hasattr(t, "matching_track")
            and t.matching_track._track is None
            and not t.is_foldable
            and t.name == base_track.name,
            SongFacade.simple_tracks(SimpleAudioTrack),
        )

    def _get_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        return AbstractMatchingTrack.get_matching_track(self._base_track)

    def _assert_valid_track_name(self):
        # type: () -> None
        instrument_names = [d.value.lower() for d in DeviceEnum if d.is_instrument]
        assert self._base_track.name.lower() not in instrument_names, "Track name is not specific"

    def _copy_params_from_base_track(self):
        # type: () -> None
        self._track = self._get_track()
        assert self._track, "no matching track"

        self._track.volume = self._base_track.volume
        self._base_track.volume = 0

        self._base_track.devices.mixer_device.copy_to(self._track.devices.mixer_device)
        self._base_track.devices.mixer_device.reset()

        devices = self._base_track.devices.all

        if len(devices) == 0:
            Backend.client().show_success("Track copied ! (no devices)")
            return

        self._base_track.select()
        ApplicationViewFacade.show_device()
        message = "Please copy %s devices" % len(devices)

        Backend.client().show_info(message)

    def switch_monitoring(self):
        # type: () -> None
        self._track.monitoring_state.switch()

    def connect_base_track(self):
        # type: () -> Optional[Sequence]
        # plug the matching track in its main audio track
        if self._track is None:
            return None

        self._base_track.color = self._track.color
        self.connect_base_track_routing()
        return None

    def connect_base_track_routing(self):
        # type: () -> None
        self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._track.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        self._base_track.output_routing.track = self._track  # type: ignore[assignment]

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
        raise Protocol0Warning("Unbouncable %s" % self)

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

        # recolor clip marked with automation
        self._track.restore_clip_color()

        if (
            len([t for t in SongFacade.simple_tracks() if t.output_routing.track == self._track])
            == 0
        ):
            self._activate_base_track()
