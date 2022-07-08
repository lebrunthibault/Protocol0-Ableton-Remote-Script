import itertools
from functools import partial

from typing import Optional, cast, List, Tuple

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import \
    AbstractTrackAppearance
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackArmState import \
    ExternalSynthTrackArmState
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import \
    ExternalSynthTrackMonitoringState
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.utils import find_if
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrack(AbstractGroupTrack):
    REMOVE_CLIPS_ON_ADDED = True

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track)
        self.midi_track = cast(SimpleMidiTrack, base_group_track.sub_tracks[0])

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
        self.arm_state = ExternalSynthTrackArmState(self.base_track, self.midi_track,
                                                    self.monitoring_state)

        self.appearance.register_observer(self)

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)

    is_armed = cast(bool, ForwardTo("arm_state", "is_armed"))
    is_partially_armed = cast(bool, ForwardTo("arm_state", "is_partially_armed"))

    def on_added(self):
        # type: () -> Sequence
        if len(self.clips):
            Backend.client().show_warning("Deleting clips ..")

        seq = Sequence()
        seq.add(self.arm_state.arm)

        for track in self.sub_tracks:
            seq.add([clip.delete for clip in track.clips])

        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        self._map_optional_audio_tail_track()
        super(ExternalSynthTrack, self).on_tracks_change()
        self.monitoring_state.set_audio_tail_track(self.audio_tail_track)
        self.monitoring_state.set_dummy_track(self.dummy_track)
        self._map_clip_slots()

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        """Launches the tail clip on last playing clip slot bar"""
        playing_cs = find_if(lambda cs: cs.is_playing, self.audio_track.clip_slots)
        if playing_cs is None \
                or playing_cs.clip is None \
                or not self.audio_tail_track:
            return

        if playing_cs.clip.playing_position.in_last_bar:
            if playing_cs.index < len(self.audio_tail_track.clip_slots):
                audio_tail_clip = self.audio_tail_track.clip_slots[playing_cs.index].clip
                if audio_tail_clip and not audio_tail_clip.is_recording:
                    audio_tail_clip.play_and_mute()

    def _map_optional_audio_tail_track(self):
        # type: () -> None
        has_tail_track = len(self.base_track.sub_tracks) > 2 and len(
            list(self.base_track.sub_tracks[2].devices)) == 0

        if has_tail_track and not self.audio_tail_track:
            track = self.base_track.sub_tracks[2]
            self.audio_tail_track = SimpleAudioTailTrack(track._track, track.index)
            self._link_sub_track(self.audio_tail_track)
            Scheduler.defer(partial(setattr, self.audio_tail_track.input_routing, "track",
                                    self.midi_track))
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
            return cast(SimpleAudioTrack, self.sub_tracks[-2]), cast(SimpleAudioTrack,
                                                                     self.sub_tracks[-1])
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
            for midi_clip_slot, audio_clip_slot in
            itertools.izip(
                self.midi_track.clip_slots, self.audio_track.clip_slots
            )
        ]

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackAppearance):
            for sub_track in self.sub_tracks:
                sub_track.appearance.color = self.appearance.color
        elif isinstance(observable, SimpleTrackDevices):
            self.external_device = find_if(lambda d: d.is_external_device,
                                           list(self.midi_track.devices))
            if self.external_device is None:
                raise Protocol0Warning("%s should have an external device" % self)

            self._instrument = self.midi_track.instrument or InstrumentMinitaur(device=None,
                                                                                track_name=self.name)
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
        for sub_track in self.sub_tracks:
            sub_track.solo = solo

    @property
    def can_change_presets(self):
        # type: () -> bool
        return len(self.audio_track.clips) == 0 or \
               not self.protected_mode_active or \
               not self.instrument.HAS_PROTECTED_MODE

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
