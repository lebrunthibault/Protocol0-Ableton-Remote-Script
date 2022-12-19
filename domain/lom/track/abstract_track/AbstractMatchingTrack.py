import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import Optional

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


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
                self._disconnect_base_track_routing()

    def _get_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        matching_track = find_if(
            lambda t: t != self._base_track
            and not t.is_foldable
            and t.name == self._base_track.name,
            SongFacade.simple_tracks(),
        )

        if isinstance(matching_track, SimpleAudioTrack):
            return matching_track

        return None

    def _get_atk_cs(self):
        # type: () -> Optional[AudioClipSlot]
        audio_track = self._base_track.sub_tracks[1]

        if len(audio_track.clips) == 0:
            raise Protocol0Warning("Audio track has no clips")

        return (
            find_if(
                lambda cs: cs.clip is not None
                and cs.clip.clip_name.base_name == ClipNameEnum.ATK.value,
                audio_track.clip_slots,
            )
            or find_if(
                lambda cs: cs.clip is not None
                and cs.clip.clip_name.base_name == ClipNameEnum.ONCE.value,
                audio_track.clip_slots,
            )
            or find_if(
                lambda cs: cs.clip is not None,
                audio_track.clip_slots,
            )
        )

    def switch_monitoring(self):
        # type: () -> None
        self._track.monitoring_state.switch()

    def connect_main_track(self):
        # type: () -> Optional[Sequence]
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(self)
        Scheduler.defer(self._connect_main_track)
        return None

    def _connect_main_track(self):
        # type: () -> Optional[Sequence]
        # plug the matching track in its main audio track
        if self._track is None:
            return None

        self.connect_base_track_routing()
        return None

    def connect_base_track_routing(self):
        # type: () -> None
        self._track.input_routing.type = InputRoutingTypeEnum.EXT_IN
        self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._base_track.output_routing.track = self._track  # type: ignore[assignment]

    def _disconnect_base_track_routing(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        self._base_track.output_routing.track = self._base_track.group_track or SongFacade.master_track()  # type: ignore[assignment]

        if (
            len([t for t in SongFacade.simple_tracks() if t.output_routing.track == self._track])
            == 0
        ):
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

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

    def disconnect(self):
        # type: () -> None
        super(AbstractMatchingTrack, self).disconnect()
        if self._track is None:
            return

        Scheduler.defer(self._disconnect_base_track_routing)
