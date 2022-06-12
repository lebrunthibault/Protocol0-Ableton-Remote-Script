from functools import partial

from typing import Optional

from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import \
    TrackRecorderExternalSynthAudio
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioMulti(TrackRecorderExternalSynthAudio):
    def legend(self, bar_length):
        # type: (int) -> str
        number_of_scenes = 1
        current_scene = self.recording_scene
        while self.recording_scene.next_scene != current_scene and \
                self.track.midi_track.clip_slots[current_scene.next_scene.index].clip:
            current_scene = current_scene.next_scene
            number_of_scenes += 1
        return "audio multi (%s scenes)" % number_of_scenes

    def record(self, _):
        # type: (float) -> Sequence
        self._clear_automation()

        self.recording_scene.fire()
        for cs in self._recording_clip_slots:
            cs.fire()
        seq = Sequence()
        seq.wait_for_event(SceneLastBarPassedEvent)
        seq.wait_beats(2)
        seq.add(self._launch_record_on_next_scene)
        return seq.done()

    def _launch_record_on_next_scene(self):
        # type: () -> Optional[Sequence]
        next_scene = self.recording_scene.next_scene
        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent)
        seq.add(partial(audio_clip.clip_name.update, ""))
        seq.done()

        if next_scene == self.recording_scene:
            return None
        if not self.track.midi_track.clip_slots[next_scene.index].clip:
            return None

        if self.track.audio_tail_track:
            # there is no tail recording in this setup
            self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip.delete()

        self.set_recording_scene_index(next_scene.index)
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in self._recording_clip_slots])
        seq.add(partial(self.record, next_scene.bar_length))
        return seq.done()
