from functools import partial

from typing import List

from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.track_recorder.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth


class TrackRecorderExternalSynthAudio(AbstractTrackRecorderExternalSynth):
    def _focus_main_clip(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(TrackRecorderExternalSynthAudio, self)._focus_main_clip)
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        if len(midi_clip.automated_parameters):
            seq.add(partial(self.parent.uiManager.show_clip_envelope_parameter, midi_clip, midi_clip.automated_parameters[0]))
        return seq.done()

    def record(self, bar_length):
        # type: (int) -> Sequence
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        self.parent.wait([1, 10, 50, 100], partial(self.parent.automationTrackManager.display_selected_parameter_automation, clip=midi_clip, show_warning=False))
        return super(TrackRecorderExternalSynthAudio, self).record(bar_length)

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.audio_track, self.track.audio_tail_track])
