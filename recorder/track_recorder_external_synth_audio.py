from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth
from protocol0.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudio(AbstractTrackRecorderExternalSynth):
    def pre_record(self):
        # type: () -> None
        if not self.track.midi_track.playable_clip:
            raise Protocol0Warning("No midi clip selected")

        self.song.metronome = False

    def on_record_cancelled(self):
        # type: () -> Sequence
        if self.track.audio_tail_track:
            self.track.audio_tail_track.playable_clip_slot.delete_clip()
        return self.track.audio_track.playable_clip_slot.delete_clip()
