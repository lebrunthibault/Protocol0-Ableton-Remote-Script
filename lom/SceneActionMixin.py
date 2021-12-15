from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import session_view_only

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


# noinspection PyTypeHints
class SceneActionMixin(object):
    def check_scene_length(self):
        # type: (Scene) -> None
        self.parent.defer(self.scene_name.update)

    def on_beat_changed(self):
        # type: (Scene) -> None
        self.scene_name.update()
        if self.current_bar == self.bar_length - 1 and self.current_beat == 2:
            self._play_audio_tails()
            self._schedule_next_scene_launch()

    @session_view_only
    def _schedule_next_scene_launch(self):
        # type: (Scene) -> None
        if self not in self.song.scenes:
            return None
        if self == self.song.looping_scene or self == self.song.scenes[-1] or self.song.scenes[self.index + 1].bar_length == 0:
            self.fire()
            seq = Sequence()
            seq.add(complete_on=self._is_triggered_listener)
            # noinspection PyUnresolvedReferences
            seq.add(self.song.notify_session_end)
            seq.done()
            return
        # this can happen when splitting a scene
        if self.length - self.playing_position <= 0:
            return

        next_scene = self.song.scenes[self.index + 1]
        next_scene.fire()

    def select(self):
        # type: (Scene) -> None
        self.song.selected_scene = self

    def fire(self):
        # type: (Scene) -> None
        if self._scene:
            self._scene.fire()

    def _stop_previous_scene(self):
        # type: (Scene) -> None
        previous_playing_scene = self.song.playing_scene
        if previous_playing_scene is None or previous_playing_scene == self:
            return

        previous_playing_scene.scene_name.update()

        # manually stopping previous scene because we don't display clip slot stop buttons
        for clip in [clip for clip in previous_playing_scene.clips if clip.track not in self.tracks]:
            if clip in previous_playing_scene.audio_tail_clips:
                continue

            clip.stop(immediate=True)

    def _play_audio_tails(self):
        # type: (Scene) -> None
        # playing tails
        if self.song.playing_scene:
            for clip in self.song.playing_scene.audio_tail_clips:
                clip.play_and_mute()

    def mute_audio_tails(self):
        # type: (Scene) -> None
        # playing tails
        if self.song.playing_scene:
            for clip in self.song.playing_scene.audio_tail_clips:
                clip.mute_if_scene_changed()

    def pre_fire(self):
        # type: (Scene) -> None
        """ when a record is fired the scene will play """
        self.fire()
        self.song.stop_playing()

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
            if previous_looping_scene:
                previous_looping_scene.scene_name.update()
            self.parent.sceneBeatScheduler.clear()  # clearing scene scheduling
        else:  # solo inactivation
            Scene.LOOPING_SCENE = None

        self.scene_name.update()

    def split(self):
        # type: (Scene) -> Optional[Sequence]
        bar_length = self.SELECTED_DUPLICATE_SCENE_BAR_LENGTH
        seq = Sequence()
        seq.add(partial(self.song.duplicate_scene, self.index))
        seq.add(lambda: self.song.selected_scene._crop_clips_to_bar_length(bar_length=-bar_length))
        seq.add(partial(self._crop_clips_to_bar_length, bar_length=bar_length))
        return seq.done()

    def _crop_clips_to_bar_length(self, bar_length):
        # type: (Scene, int) -> None
        for clip in self.clips:
            if 0 < bar_length < clip.bar_length:
                clip.bar_length = min(clip.bar_length, bar_length)
            elif bar_length < 0 and clip.bar_length > abs(bar_length):
                offset = clip.length - abs(bar_length) * self.song.signature_numerator
                clip.start_marker += offset
                clip.loop_start += offset
