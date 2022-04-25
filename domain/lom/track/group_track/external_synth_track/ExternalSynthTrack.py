import itertools
from functools import partial

from typing import Optional, cast, List, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.TrackDevices import TrackDevices
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackArmState import \
    ExternalSynthTrackArmState
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import \
    ExternalSynthTrackMonitoringState
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if, ForwardTo
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrack(AbstractGroupTrack):
    REMOVE_CLIPS_ON_ADDED = True

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track=base_group_track)
        self.midi_track = cast(SimpleMidiTrack, base_group_track.sub_tracks[0])
        self.audio_track = cast(SimpleAudioTrack, base_group_track.sub_tracks[1])
        self.midi_track.track_name.disconnect()
        self.audio_track.track_name.disconnect()
        self.audio_tail_track = None  # type: Optional[SimpleAudioTailTrack]

        # sub tracks are now handled by self
        for sub_track in base_group_track.sub_tracks:
            sub_track.abstract_group_track = self

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        self._instrument = None  # type: Optional[InstrumentInterface]
        self._external_device = None  # type: Optional[Device]
        self.midi_track.devices.register_observer(self)
        self.midi_track.devices.build()

        self.monitoring_state = ExternalSynthTrackMonitoringState(self)  # type: ExternalSynthTrackMonitoringState
        self._arm_state = ExternalSynthTrackArmState(self.base_track, self.midi_track, self.monitoring_state)
        self.arm_track = self._arm_state.arm_track   # type: ignore[assignment]
        self.unarm = self._arm_state.unarm   # type: ignore[assignment]

        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)

    is_armed = cast(bool, ForwardTo("_arm_state", "is_armed"))   # type: ignore[assignment]
    is_partially_armed = ForwardTo("_arm_state", "is_partially_armed")   # type: ignore[assignment]

    def on_added(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(ExternalSynthTrack, self).on_added)
        seq.add(self.abstract_track.arm)

        for dummy_track in self.dummy_tracks:
            seq.add([clip.delete for clip in dummy_track.clips])

        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        self._map_optional_audio_tail_track()
        super(ExternalSynthTrack, self).on_tracks_change()
        self._link_clip_slots()

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        # if it is the last bar
        playing_cs = find_if(lambda cs: cs.is_playing, self.audio_track.clip_slots)
        if playing_cs is None \
                or playing_cs.clip is None \
                or not self.audio_tail_track:
            return

        if playing_cs.clip.playing_position.in_last_bar:
            audio_tail_clip = self.audio_tail_track.clip_slots[playing_cs.index].clip
            if audio_tail_clip:
                audio_tail_clip.play_and_mute()

    def _map_optional_audio_tail_track(self):
        # type: () -> None
        has_tail_track = len(self.base_track.sub_tracks) > 2 and len(list(self.base_track.sub_tracks[2].devices)) == 0

        if has_tail_track and not self.audio_tail_track:
            track = self.base_track.sub_tracks[2]
            self.audio_tail_track = SimpleAudioTailTrack(track._track, track._index)
            self.audio_tail_track.abstract_group_track = self
            self.audio_tail_track.group_track = self.base_track
            Scheduler.defer(self.audio_tail_track.configure)
            self.audio_tail_track.track_name.disconnect()
            Scheduler.defer(partial(setattr, self.audio_tail_track, "name", SimpleAudioTailTrack.DEFAULT_NAME))
        elif not has_tail_track:
            self.audio_tail_track = None

    @classmethod
    def is_group_track_valid(cls, base_group_track):
        # type: (SimpleTrack) -> bool
        if len(base_group_track.sub_tracks) < 2:
            return False

        if not isinstance(base_group_track.sub_tracks[0], SimpleMidiTrack):
            return False
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False

        return True

    def on_scenes_change(self):
        # type: () -> None
        self._link_clip_slots()

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        main_tracks_length = 3 if self.audio_tail_track else 2
        for track in self.base_track.sub_tracks[main_tracks_length:]:
            yield track

    def _link_clip_slots(self):
        # type: () -> None
        if len(self._clip_slot_synchronizers) == len(self.midi_track.clip_slots):
            return

        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

        self._clip_slot_synchronizers = [
            ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
            for midi_clip_slot, audio_clip_slot in
            itertools.izip(  # type: ignore[attr-defined]
                self.midi_track.clip_slots, self.audio_track.clip_slots
            )
        ]

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, TrackDevices):
            self._external_device = find_if(lambda d: d.is_external_device, list(self.midi_track.devices))
            if self._external_device is None:
                raise Protocol0Warning("%s should have an external device" % self)

            if self._instrument is None:
                self._instrument = self.midi_track.instrument or InstrumentMinitaur(track=self.midi_track, device=None)
            elif self.midi_track.instrument and self.midi_track.instrument != self._instrument:
                raise Protocol0Error("Cannot switch instruments in an ExternalSynthTrack")

    @property
    def instrument(self):
        # type: () -> InstrumentInterface
        return cast(InstrumentInterface, self._instrument)

    @property
    def clips(self):
        # type: () -> List[Clip]
        clip_slots = cast(List[ClipSlot],
                          self.midi_track.clip_slots) + self.audio_track.clip_slots
        if self.audio_tail_track:
            clip_slots += self.audio_tail_track.clip_slots

        return [clip_slot.clip for clip_slot in clip_slots if clip_slot.has_clip and clip_slot.clip]

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
    def color(self):
        # type: () -> int
        return self.base_track.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.base_track.color = color_index
        for sub_track in self.sub_tracks:
            sub_track.color = color_index

    @property
    def computed_color(self):
        # type: () -> int
        return self.instrument.TRACK_COLOR.color_int_value

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

    def copy_and_paste_clips_to_new_scene(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(SongFacade.selected_scene().duplicate)
        seq.add(lambda: SongFacade.current_external_synth_track().midi_track.clip_slots[
            SongFacade.selected_scene().index].clip.crop())
        seq.add(lambda: SongFacade.current_external_synth_track().audio_track.clip_slots[
            SongFacade.selected_scene().index].clip.crop())
        seq.add()
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()
        self._clip_slot_synchronizers = []