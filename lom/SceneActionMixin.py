from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.interface.InterfaceState import InterfaceState
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import session_view_only, throttle
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


# noinspection PyTypeHints
class SceneActionMixin(object):
    @throttle(wait_time=20)
    def _check_scene_length(self):
        # type: (Scene) -> None
        self.parent.defer(self.scene_name.update)
        if self.is_playing:
            self.schedule_next_scene_launch()

    @session_view_only
    def schedule_next_scene_launch(self):
        # type: (Scene) -> None
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
            self._scene.fire()

    def toggle_solo(self):
        # type: (Scene) -> None
        """ for a scene solo means looped """
        from protocol0.lom.Scene import Scene

        if not self.looping:  # solo activation
            previous_looping_scene = Scene.LOOPING_SCENE
            self.looping = True
            if Scene.PLAYING_SCENE != self:
                self.fire()
            if previous_looping_scene:
                previous_looping_scene.scene_name.update()
            self.parent.sceneBeatScheduler.clear()  # clearing scene scheduling
        else:  # solo inactivation
            self.looping = False
            self.schedule_next_scene_launch()  # restore previous behavior of follow action
        self.scene_name.update()

    def scroll_duplicate_bar_lengths(self, go_next):
        # type: (Scene, bool) -> None
        if self.length < 2:
            self.parent.log_warning("Cannot partial duplicate scene with length %s (min 2 bars)" % self.length)
            return
        bar_lengths = []
        power = 0
        while pow(2, power) <= self.bar_length / 2:
            bar_lengths += [pow(2, power), -pow(2, power)]
            power += 1
        bar_lengths.sort()

        from protocol0.lom.Scene import Scene
        Scene.SELECTED_DUPLICATE_BAR_LENGTH = scroll_values(
            bar_lengths, Scene.SELECTED_DUPLICATE_BAR_LENGTH, go_next
        )
        InterfaceState.show_selected_bar_length(Scene.SELECTED_DUPLICATE_BAR_LENGTH)

    def split(self):
        # type: (Scene) -> Optional[Sequence]
        if self.bar_length % 2 != 0:
            self.parent.log_warning("bar length (%s) is not even, cannot split" % self.bar_length)
            return None
        bar_length = int(self.bar_length / 2)

        seq = Sequence()
        seq.add(partial(self.song.duplicate_scene, self.index))
        seq.add(lambda: self.song.selected_scene._crop_clips_to_bar_length(bar_length=-bar_length))
        seq.add(partial(self._crop_clips_to_bar_length, bar_length=bar_length))
        return seq.done()

    def partial_duplicate(self):
        # type: (Scene) -> Sequence
        from protocol0.lom.Scene import Scene

        seq = Sequence()
        seq.add(partial(self.song.duplicate_scene, self.index))
        seq.add(
            lambda: self.song.selected_scene._crop_clips_to_bar_length(bar_length=Scene.SELECTED_DUPLICATE_BAR_LENGTH))
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
