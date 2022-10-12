from functools import partial

from typing import Optional, List

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioMulti(TrackRecorderExternalSynthAudio):
    @property
    def recording_scenes(self):
        # type: () -> List[Scene]
        """A list of scenes that are going to be recorded"""
        recording_scenes = [self.recording_scene]
        while (
            self.recording_scene.next_scene != recording_scenes[-1]
            and self.track.midi_track.clip_slots[recording_scenes[-1].next_scene.index].clip
        ):
            recording_scenes.append(recording_scenes[-1].next_scene)

        return recording_scenes

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio multi (%s scenes)" % len(self.recording_scenes)

    def _pre_record(self):
        # type: () -> None
        """
        Alerting when a midi clip does not have the same bar length as its scene (except for the last one)
        In this case the audio tail might not be recorded fully due to switching scenes

        This is not usual practice the case but could be addressed by using
        the clip tail decorator to delay the recording of the next scene
        """
        super(TrackRecorderExternalSynthAudioMulti, self)._pre_record()
        scene_clip_bar_length_mismatch = False
        for scene in self.recording_scenes[:-1]:
            if (
                scene.bar_length
                != self.track.midi_track.clip_slots[scene.index].clip.bar_length
            ):
                scene_clip_bar_length_mismatch = True
                break

        if scene_clip_bar_length_mismatch:
            Backend.client().show_warning(
                "At least one midi clip has a smaller bar length than its scene. Pay attention to the tail recording"
            )

    def record(self, bar_length):
        # type: (float) -> Sequence
        self.recording_scene.fire()
        for cs in self._recording_clip_slots:
            cs.fire()
        seq = Sequence()
        if bar_length != self.recording_scene.bar_length:
            seq.wait_bars(bar_length - 1, wait_for_song_start=True)
            seq.add(self.track.midi_track.stop)
            seq.add(self.track.audio_track.stop)

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

        # No next scene or no midi clip on next scene -> recording stops
        if next_scene == self.recording_scene:
            return None
        if not self.track.midi_track.clip_slots[next_scene.index].clip:
            return None

        # If the previous clip bar length equals the scene length we remove the tail
        # as it was actually not recorded
        # Else, we keep it, because the clip is going to be looped
        if self.track.audio_tail_track:
            clip_bar_length = self.track.midi_track.clip_slots[
                self.recording_scene_index
            ].clip.bar_length

            audio_tail_clip = self.track.audio_tail_track.clip_slots[
                self.recording_scene_index
            ].clip
            # there is no tail recording in this setup
            if clip_bar_length == self.recording_scene.bar_length:
                audio_tail_clip.delete()
            else:
                audio_tail_clip.post_record(int(clip_bar_length))

        self.set_recording_scene_index(next_scene.index)
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in self._recording_clip_slots])

        midi_clip = self.track.midi_track.selected_clip_slot.clip
        seq.add(partial(self.record, midi_clip.bar_length))
        return seq.done()
