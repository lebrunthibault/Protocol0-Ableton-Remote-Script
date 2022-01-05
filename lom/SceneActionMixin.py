from functools import partial
from math import floor

from typing import TYPE_CHECKING, Optional, cast

from protocol0.components.SessionToArrangementManager import SessionToArrangementManager
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import throttle
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


# noinspection PyTypeHints
class SceneActionMixin(object):
    def select(self):
        # type: (Scene) -> None
        self.song.selected_scene = self

    def check_scene_length(self):
        # type: (Scene) -> None
        self.parent.defer(self.scene_name.update)

    def on_beat_changed(self):
        # type: (Scene) -> None
        if self.is_recording:
            return
        # trigger on last beat
        if self.current_beat == self.song.signature_numerator - 1:
            self.parent.defer(self._play_audio_tails)  # only call is here, at the end of each bar
        if self.current_bar == self.bar_length - 1:
            if SessionToArrangementManager.IS_BOUNCING or self.current_beat == self.song.signature_numerator - 1:
                self._fire_next_scene()

        if self.current_beat == 0 and not SessionToArrangementManager.IS_BOUNCING:
            self.parent.defer(self.scene_name.update)

    def _fire_next_scene(self):
        # type: (Scene) -> None
        next_scene = self.next_scene
        if SessionToArrangementManager.IS_BOUNCING:
            # unique call when bouncing
            if SessionToArrangementManager.LAST_SCENE_FIRED == self:
                return None
            else:
                SessionToArrangementManager.LAST_SCENE_FIRED = self

            if self == next_scene:
                self.song.stop_all_clips()
                self.parent.wait_bars(2, self.song.stop_playing)
                return None

        if next_scene != self:
            next_scene.fire()  # do not fire same scene as it focus it again (can loose current parameter focus)

    def fire(self):
        # type: (Scene) -> None
        # handles click sound when the previous scene plays shortly
        if self.song.playing_scene and self.song.playing_scene != self:
            self._stop_previous_scene(self.song.playing_scene)

        from protocol0.lom.Scene import Scene
        Scene.PLAYING_SCENE = self

        self._scene.fire()

    def fire_and_move_position(self):
        # type: (Scene) -> Sequence
        self.song.stop_playing()
        seq = Sequence()

        from protocol0.lom.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION >= self.bar_length:
            Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = 0

        # removing click when changing position
        master_volume = self.song.master_track.volume
        self.song.master_track.volume = 0
        seq.add(wait=1)
        # leveraging throttle to disable the next update (that would be 1 / *)
        seq.add(partial(self.scene_name.update, bar_position=Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION))
        seq.add(self.fire)
        seq.add(wait=1)
        seq.add(partial(self.jump_to_bar, Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION))
        seq.add(self.song.stop_playing)
        seq.add(partial(setattr, self.song.master_track, "volume", master_volume))
        seq.add(wait=1)
        seq.add(self.song.continue_playing)
        return seq.done()

    def pre_fire(self):
        # type: (Scene) -> Sequence
        self.fire()
        self.song.stop_playing()
        seq = Sequence()
        seq.add(wait=2)
        return seq.done()

    def _stop_previous_scene(self, previous_playing_scene, immediate=False):
        # type: (Scene, Scene, bool) -> None
        # manually stopping previous scene because we don't display clip slot stop buttons
        for track in previous_playing_scene.tracks:
            if not track.is_playing or track in self.tracks or isinstance(track, SimpleAudioTailTrack):
                continue

            track.stop(immediate=immediate)

        self.parent.wait_beats(1, partial(previous_playing_scene.scene_name.update, display_bar_count=False))

    def _play_audio_tails(self):
        # type: (Scene) -> None
        # playing tails
        for clip in self.audio_tail_clips:
            if clip.is_playing:
                return None
            if (self.current_bar + 1) % clip.midi_clip.bar_length != 0:
                continue

            abstract_track = cast(ExternalSynthTrack, clip.track.abstract_track)
            # do not trigger tail on monophonic loop
            if abstract_track.instrument.MONOPHONIC and self.next_scene != self and self.next_scene.clip_slots[clip.track.index - 1].clip:
                continue
            if abstract_track.midi_track.clip_slots[clip.index].clip.muted:
                continue
            else:
                clip.play_and_mute()

    def mute_audio_tails(self):
        # type: (Scene) -> None
        for clip in self.audio_tail_clips:
            clip.muted = True

    def delete(self):
        # type: (Scene) -> Optional[Sequence]
        if self._scene and not self.deleted:  # type: ignore[has-type]
            self.deleted = True
            return self.song.delete_scene(self.index)
        return None

    def toggle_loop(self):
        # type: (Scene) -> None
        """ for a scene solo means looped """
        from protocol0.lom.Scene import Scene

        if self != self.song.looping_scene:  # solo activation
            previous_looping_scene = self.song.looping_scene
            Scene.LOOPING_SCENE = self
            if self != self.song.playing_scene:
                self.fire()
            if previous_looping_scene and previous_looping_scene != self:
                previous_looping_scene.scene_name.update()
        else:  # solo inactivation
            Scene.LOOPING_SCENE = None

        self.scene_name.update()

    def split(self):
        # type: (Scene) -> Sequence
        bar_length = self.SELECTED_DUPLICATE_SCENE_BAR_LENGTH
        seq = Sequence()
        seq.add(partial(self.song.duplicate_scene, self.index))
        seq.add(lambda: self.song.selected_scene._crop_clips_to_bar_length(bar_length=-bar_length))
        seq.add(partial(self._crop_clips_to_bar_length, bar_length=bar_length))
        for track in self.song.external_synth_tracks:
            if track.audio_tail_track and track.audio_tail_track.clip_slots[self.index]:
                seq.add([track.audio_tail_track.clip_slots[self.index].clip.delete])
        return seq.done()

    def _crop_clips_to_bar_length(self, bar_length):
        # type: (Scene, int) -> None
        for clip in self.clips:
            if isinstance(clip.track, SimpleAudioTailTrack):
                continue

            if 0 < bar_length < clip.bar_length:
                clip.bar_length = min(clip.bar_length, bar_length)
            elif bar_length < 0 and clip.bar_length > abs(bar_length):
                offset = clip.length - abs(bar_length) * self.song.signature_numerator
                clip.start_marker += offset
                clip.loop_start += offset

    @throttle(wait_time=10)
    def scroll_position(self, go_next):
        # type: (Scene, bool) -> None
        from protocol0.lom.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE != self:
            Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = 0
            Scene.LAST_MANUALLY_STARTED_SCENE = self
        scene_position = Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION

        if self.has_playing_clips:
            bar_position = self.playing_position * self.song.signature_numerator
            rounded_bar_position = floor(bar_position) if go_next else round(bar_position)
            scene_position = int(scroll_values(range(0, self.bar_length), rounded_bar_position, go_next=go_next))
            self.jump_to_bar(scene_position)
        else:
            scene_position = scroll_values(range(0, self.bar_length), scene_position, go_next=go_next)

        Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = scene_position
        self.scene_name.update(bar_position=scene_position)

    def jump_to_bar(self, bar_position):
        # type: (Scene, float) -> None
        beat_offset = (bar_position * self.song.signature_numerator) - self.playing_position
        self.song.scrub_by(beat_offset)
