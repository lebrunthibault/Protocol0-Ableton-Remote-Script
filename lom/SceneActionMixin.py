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
        if self.is_playing:
            self.schedule_next_scene_launch()

    @session_view_only
    def schedule_next_scene_launch(self):
        # type: (Scene) -> None
        if self not in self.song.scenes:
            return None
        if self.looping or self == self.song.scenes[-1] or self.song.scenes[self.index + 1].bar_length == 0:
            # noinspection PyUnresolvedReferences
            self.parent.sceneBeatScheduler.wait_beats(self.length - self.playing_position, self.song.notify_session_end)
            return
        # this can happen when splitting a scene
        if self.length - self.playing_position <= 0:
            return

        next_scene = self.song.scenes[self.index + 1]
        self.parent.sceneBeatScheduler.wait_beats(self.length - self.playing_position - 1, next_scene.fire)

    def select(self):
        # type: (Scene) -> None
        self.song.selected_scene = self

    def fire(self):
        # type: (Scene) -> None
        if self._scene:
            self.stop_previous_scene()
            self._scene.fire()

    def stop_previous_scene(self, immediate=False):
        # type: (Scene, bool) -> None
        from protocol0.lom.Scene import Scene
        previous_playing_scene = Scene.PLAYING_SCENE
        if previous_playing_scene and previous_playing_scene != self:
            self.parent.defer(previous_playing_scene.scene_name.update)
            # manually stopping previous scene because we don't display clip slot stop buttons
            for clip in previous_playing_scene.clips:
                if clip.is_playing and clip.track not in self.tracks:
                    if immediate:
                        self.parent.defer(partial(clip.track.stop, immediate=True))
                    else:
                        clip.track.stop()

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

        if not self.looping:  # solo activation
            previous_looping_scene = Scene.LOOPING_SCENE
            Scene.LOOPING_SCENE = self
            if Scene.PLAYING_SCENE != self:
                self.fire()
            if previous_looping_scene:
                previous_looping_scene.scene_name.update()
            self.parent.sceneBeatScheduler.clear()  # clearing scene scheduling
        else:  # solo inactivation
            self.looping = False
            self.schedule_next_scene_launch()  # restore previous behavior of follow action
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
