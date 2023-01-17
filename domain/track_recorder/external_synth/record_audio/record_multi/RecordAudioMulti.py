from functools import partial

from typing import Optional

from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.shared.sequence.Sequence import Sequence


class RecordAudioMulti(RecordProcessorInterface):
    def process(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> Sequence
        config.recording_scene.fire()
        for cs in config.clip_slots:
            cs.fire()
        seq = Sequence()
        if config.bar_length != config.recording_scene.bar_length:
            seq.wait_bars(config.bar_length - 1, wait_for_song_start=True)
            seq.add(track.midi_track.stop)
            seq.add(track.audio_track.stop)

        seq.wait_for_event(SceneLastBarPassedEvent)
        seq.wait_beats(2)
        seq.add(self._launch_record_on_next_scene)
        return seq.done()

    def _launch_record_on_next_scene(self, track, config):
        # type: (ExternalSynthTrack, RecordConfig) -> Optional[Sequence]
        next_scene = config.recording_scene.next_scene
        audio_clip = track.audio_track.clip_slots[config.recording_scene].clip

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent)
        seq.add(partial(audio_clip.clip_name.update, ""))
        seq.done()

        # No next scene or no midi clip on next scene -> recording stops
        if next_scene == config.recording_scene:
            return None
        if not track.midi_track.clip_slots[next_scene.index].clip:
            return None

        # pass to the next scene
        config.scene_index = next_scene.index
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in config.clip_slots])
        seq.add(partial(self.process, track, config))

        return seq.done()
