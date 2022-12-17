from typing import List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingEndedEvent import (
    ExternalSynthAudioRecordingEndedEvent,
)
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingStartedEvent import (
    ExternalSynthAudioRecordingStartedEvent,
)
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthMixin import (
    TrackRecorderExternalSynthMixin,
)
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudio(TrackRecorderExternalSynthMixin, AbstractTrackRecorder):
    def legend(self, bar_length):
        # type: (int) -> str
        return "audio %s bars" % str(bar_length)

    def _pre_record(self):
        # type: () -> None
        super(TrackRecorderExternalSynthAudio, self)._pre_record()
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        if midi_clip.loop.start != 0:
            Backend.client().show_warning("Cropping midi clip")
            midi_clip.crop()
        DomainEventBus.emit(ExternalSynthAudioRecordingStartedEvent(self.track))

    def record(self, bar_length):
        # type: (float) -> Sequence
        # negative delay so that it's not late
        return super(TrackRecorderExternalSynthAudio, self).record(bar_length - 0.6)

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.audio_track, self.track.audio_tail_track])

    def _post_record(self):
        # type: () -> None
        super(TrackRecorderExternalSynthAudio, self)._post_audio_record()
        DomainEventBus.emit(ExternalSynthAudioRecordingEndedEvent(self.track))
