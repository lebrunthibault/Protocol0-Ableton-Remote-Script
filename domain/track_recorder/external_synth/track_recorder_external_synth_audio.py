from functools import partial

from typing import List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingEndedEvent import \
    ExternalSynthAudioRecordingEndedEvent
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingStartedEvent import \
    ExternalSynthAudioRecordingStartedEvent
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_mixin import TrackRecorderExternalSynthMixin
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudio(TrackRecorderExternalSynthMixin, AbstractTrackRecorder):
    def legend(self, bar_length):
        # type: (int) -> str
        return "audio %s bars" % str(bar_length)

    def _pre_record(self):
        # type: () -> None
        super(TrackRecorderExternalSynthAudio, self)._pre_record()
        SongFacade.usamo_device().device_on = True
        DomainEventBus.notify(ExternalSynthAudioRecordingStartedEvent(self.track))

    def _focus_main_clip(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(TrackRecorderExternalSynthAudio, self)._focus_main_clip)
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        if len(midi_clip.automated_parameters):
            seq.add(partial(midi_clip.show_parameter_envelope, midi_clip.automated_parameters[0]))
        return seq.done()

    def record(self, bar_length):
        # type: (float) -> Sequence
        self._clear_automation()
        # negative delay so that it's not late
        return super(TrackRecorderExternalSynthAudio, self).record(bar_length - 0.6)

    def _clear_automation(self):
        # type: () -> None
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        # reset automation envelopes
        midi_clip.clear_all_envelopes()
        if len(midi_clip.automated_parameters):
            for tick in [1, 10, 50, 100]:
                Scheduler.wait(tick, midi_clip.display_current_parameter_automation)

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.audio_track, self.track.audio_tail_track])

    def post_audio_record(self):
        # type: () -> None
        super(TrackRecorderExternalSynthAudio, self).post_audio_record()
        DomainEventBus.notify(ExternalSynthAudioRecordingEndedEvent(self.track))
