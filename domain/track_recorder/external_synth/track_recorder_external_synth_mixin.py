from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder


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
        ApplicationView.show_device()

    # noinspection PyTypeHints,PyArgumentList
    def _post_record(self):
        # type: (AbstractTrackRecorder) -> None
        from typing import cast
        track = cast(ExternalSynthTrack, self.track)
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        for tick in [1, 10, 50, 100]:
            Scheduler.wait(tick, self._song.re_enable_automation)

        midi_clip = track.midi_track.clip_slots[self.recording_scene_index].clip
        audio_clip = track.audio_track.clip_slots[self.recording_scene_index].clip
        if not midi_clip or not audio_clip:
            return None

        audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)

        midi_clip.select()
        midi_clip.show_loop()
