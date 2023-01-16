import time
from functools import partial

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import subject_slot
from typing import Optional, cast, List, Dict

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthMatchingTrack import (
    ExternalSynthMatchingTrack,
)
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackArmState import (
    ExternalSynthTrackArmState,
)
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackDummyGroup import (
    ExternalSynthTrackDummyGroup,
)
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import (  # noqa
    ExternalSynthTrackMonitoringState,
)
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrack(AbstractGroupTrack):
    REMOVE_CLIPS_ON_ADDED = True

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track)
        self.base_track = cast(SimpleAudioTrack, base_group_track)
        midi_track = base_group_track.sub_tracks[0]
        self.midi_track = SimpleMidiExtTrack(midi_track._track, midi_track.index)
        self.link_sub_track(self.midi_track)

        audio_track = base_group_track.sub_tracks[1]
        self.audio_track = SimpleAudioExtTrack(audio_track._track, audio_track.index)
        self.link_sub_track(self.audio_track)

        self.audio_tail_track = None  # type: Optional[SimpleAudioTailTrack]
        self.dummy_group = ExternalSynthTrackDummyGroup(self)  # type: ExternalSynthTrackDummyGroup
        self.matching_track = ExternalSynthMatchingTrack(self.base_track)

        # sub tracks are now handled by self
        for sub_track in base_group_track.sub_tracks:
            sub_track.abstract_group_track = self

        self._instrument = None  # type: Optional[InstrumentInterface]
        self.external_device = None  # type: Optional[Device]
        self.midi_track.devices.register_observer(self)
        self.midi_track.devices.build()

        self.monitoring_state = ExternalSynthTrackMonitoringState(
            self.midi_track,
            self.audio_track,
            self.audio_tail_track,
            self.dummy_group,
            self.matching_track,
            cast(Device, self.external_device),
        )  # type: ExternalSynthTrackMonitoringState
        self.arm_state = ExternalSynthTrackArmState(self.base_track, self.midi_track)
        self.arm_state.register_observer(self.matching_track)
        self.arm_state.register_observer(self.monitoring_state)

        # this is necessary to monitor the group track solo state
        self._un_soloed_at = time.time()  # type: float

        self._force_clip_colors = False

    is_armed = cast(bool, ForwardTo("arm_state", "is_armed"))
    is_partially_armed = cast(bool, ForwardTo("arm_state", "is_partially_armed"))

    def on_tracks_change(self):
        # type: () -> None
        self._map_optional_audio_tail_track()
        super(ExternalSynthTrack, self).on_tracks_change()
        self.monitoring_state.set_audio_tail_track(self.audio_tail_track)

        self._sub_track_solo_listener.replace_subjects(
            [sub_track._track for sub_track in self.sub_tracks]
        )

    def _map_optional_audio_tail_track(self):
        # type: () -> None
        has_tail_track = (
            len(self.base_track.sub_tracks) > 2
            and len(list(self.base_track.sub_tracks[2].devices)) == 0
        )

        if has_tail_track and not self.audio_tail_track:
            track = self.base_track.sub_tracks[2]
            self.audio_tail_track = SimpleAudioTailTrack(track._track, track.index)
            self.link_sub_track(self.audio_tail_track)
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

        midi_track = base_group_track.sub_tracks[0]
        if not isinstance(midi_track, SimpleMidiTrack):
            return False
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False

        if midi_track.instrument is not None and not midi_track.instrument.IS_EXTERNAL_SYNTH:
            return False

        return True

    def route_sub_tracks(self):
        # type: () -> None
        """Overriding this because parent method doesn't take arm state into account"""
        super(ExternalSynthTrack, self).route_sub_tracks()
        if self.is_armed:
            self.monitoring_state.monitor_midi()
        else:
            self.monitoring_state.monitor_audio()

    def update(self, observable):
        # type: (Observable) -> None
        super(ExternalSynthTrack, self).update(observable)
        if isinstance(observable, SimpleTrackDevices):
            self.external_device = find_if(
                lambda d: d.is_external_device, list(self.midi_track.devices)
            )
            if self.external_device is None:
                raise Protocol0Warning("%s should have an external device" % self)

            self._instrument = self.midi_track.instrument or InstrumentMinitaur(
                device=None, track_name=self.name
            )

    @property
    def instrument_track(self):
        # type: () -> SimpleTrack
        return self.midi_track

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        if ApplicationViewFacade.is_clip_view_visible():
            return self.midi_track
        else:
            return super(ExternalSynthTrack, self).get_view_track(scene_index)

    @property
    def instrument(self):
        # type: () -> InstrumentInterface
        return cast(InstrumentInterface, self._instrument)

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self.midi_track.clip_slots

    def has_same_clips(self, track):
        # type: (AbstractTrack) -> bool
        return isinstance(track, ExternalSynthTrack) and self.midi_track.has_same_clips(
            track.midi_track
        )

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
        super(ExternalSynthTrack, self)._solo_listener()
        if not self.solo:
            self._un_soloed_at = time.time()

    @subject_slot_group("solo")
    @defer
    def _sub_track_solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        """We want to solo only the base track"""
        if track.solo and not self.dummy_group.live_track_belongs(track):
            track.solo = False  # noqa

            if self.solo:
                self.solo = False
            else:
                # Case : when the group track is soloed
                # and we want to un_solo it by toggling the solo state on the sub track
                # the group track is going to be un_soloed.
                # we need to check if it was un_soloed very recently meaning we should leave it like this
                # or not meaning we should solo it
                duration_since_last_un_solo = time.time() - self._un_soloed_at
                Logger.info("duration since last un solo: %s" % duration_since_last_un_solo)
                self.solo = duration_since_last_un_solo > 0.3

    def bars_left(self, scene_index):
        # type: (int) -> int
        if self.audio_track.is_playing:
            return self.audio_track.playing_clip.playing_position.bars_left
        else:
            return 0

    def fire(self, scene_index):
        # type: (int) -> None
        super(ExternalSynthTrack, self).fire(scene_index)

        midi_clip = self.midi_track.clip_slots[scene_index].clip
        if midi_clip is None or midi_clip.muted:
            return

        midi_clip.fire()
        if not self.is_recording:
            audio_clip = self.audio_track.clip_slots[scene_index].clip
            if audio_clip is not None:
                audio_clip.fire()

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        """
        Will stop the track immediately or quantized
        the scene_index is useful for fine tuning the stop of abstract group tracks
        """
        super(ExternalSynthTrack, self).stop(scene_index, next_scene_index, immediate=immediate)

        self.audio_track.stop(
            scene_index=scene_index, next_scene_index=next_scene_index, immediate=immediate
        )

    def prepare_for_scrub(self, scene_index):
        # type: (int) -> None
        """
        when scrubbing playback (handling FireSceneToPositionCommand)
        the audio clip need to be looping else it will stop on scrub_by
        and have the same length as the midi clip
        """
        midi_clip = self.midi_track.clip_slots[scene_index].clip
        audio_clip = self.audio_track.clip_slots[scene_index].clip
        if midi_clip is None or audio_clip is None:
            return None

        midi_clip_bar_length = midi_clip.bar_length
        try:
            audio_clip.set_temporary_length(midi_clip_bar_length)
        except IndexError:
            Backend.client().show_warning("%s: invalid clip length" % self)
            return None

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        automated_parameters = super(ExternalSynthTrack, self).get_automated_parameters(scene_index)
        automated_parameters.update(self.midi_track.get_automated_parameters(scene_index))

        return automated_parameters

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

        self.matching_track.disconnect()
