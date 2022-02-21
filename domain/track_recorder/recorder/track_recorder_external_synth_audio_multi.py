from functools import partial

from typing import Optional, Any

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth_audio import TrackRecorderExternalSynthAudio
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioMulti(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioMulti, self).__init__(*a, **k)
        Scene.LOOPING_SCENE = None

    def legend(self, bar_length):
        # type: (int) -> str
        number_of_scenes = 1
        current_scene = SongFacade.scenes()[self.recording_scene_index]
        while current_scene.next_scene != current_scene and self.track.midi_track.clip_slots[current_scene.next_scene.index].clip:
            current_scene = current_scene.next_scene
            number_of_scenes += 1
        return "audio multi (%s scenes)" % number_of_scenes

    def record(self, _):
        # type: (float) -> Sequence
        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        # reset automation enveloppes
        midi_clip.clear_all_envelopes()
        if len(midi_clip.automated_parameters):
            for tick in [1, 10, 50, 100]:
                Scheduler.wait(tick, midi_clip.display_current_parameter_automation)

        # negative delay so that it's not late
        SongFacade.scenes()[self.recording_scene_index].fire()
        for cs in self._recording_clip_slots:
            cs.fire()
        seq = Sequence()
        seq.add(wait_for_event=SceneLastBarPassedEvent)
        seq.add(wait_for_event=LastBeatPassedEvent)
        seq.add(self._launch_record_on_next_scene)
        return seq.done()

    def _launch_record_on_next_scene(self):
        # type: () -> Optional[Sequence]
        current_scene = SongFacade.scenes()[self.recording_scene_index]
        next_scene = current_scene.next_scene
        if next_scene == current_scene:
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
