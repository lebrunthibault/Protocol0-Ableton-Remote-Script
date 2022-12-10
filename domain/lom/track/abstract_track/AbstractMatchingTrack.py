import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager
from typing import Optional

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
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

        solo_tracks = [self._base_track._track]
        if self._track is not None:
            solo_tracks.append(self._track._track)
        self._solo_listener.replace_subjects(solo_tracks)

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
                self.disconnect_base_track_routing()

    def _get_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        matching_track = find_if(
            lambda t:  t != self._base_track and not t.is_foldable and t.name == self._base_track.name,
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
            or audio_track.clips[0]
        )

    def switch_monitoring(self):
        # type: () -> None
        self._track.monitoring_state.switch()

    def connect_base_track_routing(self):
        # type: () -> None
        self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._base_track.output_routing.track = self._track  # type: ignore[assignment]

    def disconnect_base_track_routing(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        if self._track is not None:
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

    def connect_main_track(self):
        # type: () -> Optional[Sequence]
        Scheduler.defer(self._connect_main_track)
        return None

    def _connect_main_track(self, _=True):
        # type: (bool) -> Optional[Sequence]
        # plug the matching track in its main audio track
        if self._track is None:
            return None

        self.connect_base_track_routing()
        return None

    @subject_slot_group("solo")
    @defer
    def _solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        self._base_track.solo = track.solo
        if self._track is not None:
            self._track.solo = track.solo
