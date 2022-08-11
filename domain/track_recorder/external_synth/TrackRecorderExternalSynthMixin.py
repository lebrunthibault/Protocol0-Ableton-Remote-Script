from functools import partial

from typing import cast

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder


class TrackRecorderExternalSynthMixin(object):
    # noinspection PyTypeHints,PyArgumentList
    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> ExternalSynthTrack
        # noinspection PyTypeChecker
        return self._track

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        return self.track.midi_track

    def _pre_record(self):
        # type: () -> None
        self.track.monitoring_state.monitor_midi()
        self.track.midi_track.select()
        ApplicationViewFacade.show_device()

    # noinspection PyTypeHints,PyArgumentList
    def _post_audio_record(self):
        # type: (AbstractTrackRecorder) -> None
        track = cast(ExternalSynthTrack, self.track)
        midi_clip_slot = track.midi_track.clip_slots[self.recording_scene_index]
        midi_clip = midi_clip_slot.clip
        audio_clip = track.audio_track.clip_slots[self.recording_scene_index].clip
        if not midi_clip or not audio_clip:
            return None

        track.midi_track.select_clip_slot(midi_clip_slot._clip_slot)
        midi_clip.show_loop()
        Scheduler.wait(10, partial(midi_clip.clip_name.update, ""))
        Scheduler.wait(10, partial(audio_clip.clip_name.update, ""))

    # noinspection PyTypeHints,PyArgumentList
    def _post_record(self):
        # type: (AbstractTrackRecorder) -> None
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        for tick in [1, 10, 50, 100]:
            Scheduler.wait(tick, self._playback_component.re_enable_automation)
