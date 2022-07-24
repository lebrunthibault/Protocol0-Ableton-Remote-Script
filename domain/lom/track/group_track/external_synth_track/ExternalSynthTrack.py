import itertools
import time
from functools import partial

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import subject_slot
from typing import Optional, cast, List, Tuple

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackArmState import (
    ExternalSynthTrackArmState,
)
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import (
    ExternalSynthTrackMonitoringState,
)
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import defer
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrack(AbstractGroupTrack):
    REMOVE_CLIPS_ON_ADDED = True

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track)
        midi_track = base_group_track.sub_tracks[0]
        self.midi_track = SimpleMidiExtTrack(midi_track._track, midi_track.index)
        self._link_sub_track(self.midi_track)

        audio_track = base_group_track.sub_tracks[1]
        self.audio_track = SimpleAudioExtTrack(audio_track._track, audio_track.index)
        self._link_sub_track(self.audio_track)

        self.audio_tail_track = None  # type: Optional[SimpleAudioTailTrack]

        # sub tracks are now handled by self
        for sub_track in base_group_track.sub_tracks:
            sub_track.abstract_group_track = self

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        self._instrument = None  # type: Optional[InstrumentInterface]
        self.external_device = None  # type: Optional[Device]
        self.midi_track.devices.register_observer(self)
        self.midi_track.devices.build()

        self.monitoring_state = ExternalSynthTrackMonitoringState(
            self.midi_track,
            self.audio_track,
            self.audio_tail_track,
            self.dummy_track,
            cast(Device, self.external_device),
        )  # type: ExternalSynthTrackMonitoringState
        self.arm_state = ExternalSynthTrackArmState(
            self.base_track, self.midi_track, self.monitoring_state
        )

        self.appearance.register_observer(self)

        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)

        self._solo_listener.subject = self._track
        # this is necessary to monitor the group track solo state
        self._un_soloed_at = None  # type: Optional[float]

    is_armed = cast(bool, ForwardTo("arm_state", "is_armed"))
    is_partially_armed = cast(bool, ForwardTo("arm_state", "is_partially_armed"))

    def on_added(self):
        # type: () -> Sequence
        if len(self.clips):
            Backend.client().show_warning("Deleting clips ..")

        self.instrument.force_show = True

        seq = Sequence()
        seq.add(self.arm_state.arm)

        for track in self.sub_tracks:
            seq.add([clip.delete for clip in track.clips])

        if self.dummy_track:
            seq.add(self.dummy_track.delete)

        if self.dummy_return_track:
            seq.add(self.dummy_return_track.delete)

        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        self._map_optional_audio_tail_track()
        super(ExternalSynthTrack, self).on_tracks_change()
        self.monitoring_state.set_audio_tail_track(self.audio_tail_track)
        self.monitoring_state.set_dummy_track(self.dummy_track)
        self._map_clip_slots()

        self._sub_track_solo_listener.replace_subjects(
            [sub_track._track for sub_track in self.sub_tracks]
        )

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        """Launches the tail clip on last playing clip slot beat"""
        audio_cs = find_if(lambda cs: cs.is_playing, self.audio_track.clip_slots)

        if audio_cs is None or audio_cs.clip is None or not self.audio_tail_track:
            return

        debug = False

        if audio_cs.clip.playing_position.in_last_bar:
            audio_tail_cs = self.audio_tail_track.clip_slots[audio_cs.index]
            audio_tail_clip = self.audio_tail_track.clip_slots[audio_cs.index].clip
            if debug:
                Logger.warning(
                    ("playing scene", SongFacade.playing_scene(), SongFacade.playing_scene().index)
                )
                Logger.warning(("audio_cs", audio_cs, audio_cs.index))
                Logger.warning(("audio_cs.clip", audio_cs.clip, audio_cs.clip.index))
                Logger.warning(("audio_tail cs", audio_tail_cs, audio_tail_cs.index))

            if audio_tail_clip and not audio_tail_clip.is_recording:
                if audio_tail_clip.index != audio_cs.index:
                    Logger.error(
                        "Index mismatch for audio tail clip. Got audio index: %s and audio tail index: %s. For %s"
                        % (audio_cs.index, audio_tail_clip.index, self), show_notification=False
                    )
                    raise Protocol0Warning("Tail clip index mismatch for %s" % self)
                if debug:
                    Logger.warning(("audio_tail clip", audio_tail_clip, audio_tail_clip.index))
                audio_tail_clip.play_and_mute()

    def _map_optional_audio_tail_track(self):
        # type: () -> None
        has_tail_track = (
            len(self.base_track.sub_tracks) > 2
            and len(list(self.base_track.sub_tracks[2].devices)) == 0
        )

        if has_tail_track and not self.audio_tail_track:
            track = self.base_track.sub_tracks[2]
            self.audio_tail_track = SimpleAudioTailTrack(track._track, track.index)
            self._link_sub_track(self.audio_tail_track)
            Scheduler.defer(
                partial(setattr, self.audio_tail_track.input_routing, "track", self.midi_track)
            )
            Scheduler.defer(self.audio_tail_track.configure)
        elif not has_tail_track:
            self.audio_tail_track = None

    @classmethod
    def is_group_track_valid(cls, base_group_track):
        # type: (SimpleTrack) -> bool
        if len(base_group_track.sub_tracks) < 2:
            return False

        if any(track.is_foldable for track in base_group_track.sub_tracks):
            return False

        if not isinstance(base_group_track.sub_tracks[0], SimpleMidiTrack):
            return False  # type: ignore[unreachable]
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False  # type: ignore[unreachable]

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False  # type: ignore[unreachable]

        return True

    def on_scenes_change(self):
        # type: () -> None
        self._map_clip_slots()

    def _get_dummy_tracks(self):
        # type: () -> Tuple[Optional[SimpleAudioTrack], Optional[SimpleAudioTrack]]
        main_tracks_length = 3 if self.audio_tail_track else 2

        if len(self.sub_tracks) == main_tracks_length + 2:
            assert isinstance(self.sub_tracks[-2], SimpleAudioTrack)
            assert isinstance(self.sub_tracks[-1], SimpleAudioTrack)
            return cast(SimpleAudioTrack, self.sub_tracks[-2]), cast(
                SimpleAudioTrack, self.sub_tracks[-1]
            )
        if len(self.sub_tracks) >= main_tracks_length + 1:
            assert isinstance(self.sub_tracks[-1], SimpleAudioTrack)
            dummy_track = cast(SimpleAudioTrack, self.sub_tracks[-1])
            # is it the dummy return track ?
            if self.sub_tracks[-1].output_routing.type == OutputRoutingTypeEnum.SENDS_ONLY:
                return None, dummy_track
            else:
                return dummy_track, None

        return None, None

    def _route_sub_tracks(self):
        # type: () -> None
        """Overriding this because parent method doesn't take arm state into account"""
        super(ExternalSynthTrack, self)._route_sub_tracks()
        if self.is_armed:
            self.monitoring_state.monitor_midi()
        else:
            self.monitoring_state.monitor_audio()

    def _map_clip_slots(self):
        # type: () -> None
        if len(self._clip_slot_synchronizers) == len(self.midi_track.clip_slots):
            return

        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

        self._clip_slot_synchronizers = [
            ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
            for midi_clip_slot, audio_clip_slot in itertools.izip(
                self.midi_track.clip_slots, self.audio_track.clip_slots
            )
        ]

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackAppearance):
            for sub_track in self.sub_tracks:
                sub_track.appearance.color = self.appearance.color
        elif isinstance(observable, SimpleTrackDevices):
            self.external_device = find_if(
                lambda d: d.is_external_device, list(self.midi_track.devices)
            )
            if self.external_device is None:
                raise Protocol0Warning("%s should have an external device" % self)

            self._instrument = self.midi_track.instrument or InstrumentMinitaur(
                device=None, track_name=self.name
            )
        else:
            raise Protocol0Error("Unmatched observable: %s" % observable)

    @property
    def instrument_track(self):
        # type: () -> SimpleTrack
        return self.midi_track

    @property
    def instrument(self):
        # type: () -> InstrumentInterface
        return cast(InstrumentInterface, self._instrument)

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self.midi_track.clip_slots

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi_track.is_playing or self.audio_track.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi_track.is_recording or self.audio_track.is_recording

    @property
    def solo(self):
        # type: () -> bool
        return super(ExternalSynthTrack, self).solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self.base_track.solo = solo

    @subject_slot("solo")
    def _solo_listener(self):
        # type: () -> None
        """We want to solo only the base track"""
        if not self.solo:
            self._un_soloed_at = time.time()

    @subject_slot_group("solo")
    @defer
    def _sub_track_solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        """We want to solo only the base track"""
        if track.solo:
            track.solo = False
            # when soloing a sub track, the group track is un soloed so we need to handle this case
            if self._un_soloed_at is not None and time.time() - self._un_soloed_at < 0.3:
                self.solo = False
            else:
                self.solo = True

    @property
    def can_change_presets(self):
        # type: () -> bool
        return (
            len(self.audio_track.clips) == 0
            or not self.protected_mode_active
            or not self.instrument.HAS_PROTECTED_MODE
        )

    def disable_protected_mode(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.prompt("Disable protected mode ?")
        seq.add(partial(setattr, self, "protected_mode_active", False))
        seq.add(partial(StatusBar.show_message, "track protected mode disabled"))
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()
        self._clip_slot_synchronizers = []
