from functools import partial

from typing import TYPE_CHECKING

from a_protocol_0.interface.InterfaceState import InterfaceState
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    from a_protocol_0.lom.Scene import Scene


class SceneActionMixin(object):
    @defer
    def _check_scene_length(self):
        # type: (Scene) -> None
        self.scene_name.update()
        self.schedule_next_scene_launch()

    def schedule_next_scene_launch(self):
        # type: (Scene) -> None
        self.parent.sceneBeatScheduler.clear()
        if self == self.song.scenes[-1] or self.looping or self.song.scenes[self.index + 1].bar_length == 0:
            return
        next_scene = self.song.scenes[self.index + 1]
        self.parent.sceneBeatScheduler.wait_beats(self.length - self.playing_position, next_scene.fire)

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
        from a_protocol_0.lom.Scene import Scene

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

    def partial_duplicate(self):
        # type: (Scene) -> Sequence
        seq = Sequence()
        seq.add(partial(self.song.duplicate_scene, self.index))
        seq.add(lambda: self.song.selected_scene._crop_clips_to_duplicate_bar_length())
        return seq.done()

    def _crop_clips_to_duplicate_bar_length(self):
        # type: (Scene) -> None
        bar_length = InterfaceState.SELECTED_DUPLICATE_BAR_LENGTH
        for clip in self.clips:
            if bar_length > 0 and clip.bar_length > bar_length:
                clip.bar_length = min(clip.bar_length, bar_length)
            elif bar_length < 0 and clip.bar_length > abs(bar_length):
                offset = clip.length - abs(bar_length) * self.song.signature_numerator
                clip.start_marker += offset
                clip.loop_start += offset
