from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.scene.SceneWindow import SceneWindow
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


# noinspection PyTypeHints
class SceneActionMixin(object):
    def select(self):
        # type: (Scene) -> None
        self._song.selected_scene = self

    def check_scene_length(self):
        # type: (Scene) -> None
        Scheduler.defer(self.scene_name.update)

    def on_last_beat(self):
        # type: (Scene) -> None
        if SongFacade.is_recording():
            return

        if self.playing_position.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

    def fire(self):
        # type: (Scene) -> None
        # handles click sound when the previous scene plays shortly
        playing_scene = SongFacade.playing_scene()
        if playing_scene and playing_scene != self:
            self._stop_previous_scene(playing_scene)

        from protocol0.domain.lom.scene.Scene import Scene
        Scene.PLAYING_SCENE = self

        self._scene.fire()

    def pre_fire(self):
        # type: (Scene) -> Sequence
        self.fire()
        self._song.stop_playing()
        seq = Sequence()
        seq.wait(2)
        return seq.done()

    def _stop_previous_scene(self, previous_playing_scene, immediate=False):
        # type: (Scene, Scene, bool) -> None
        # manually stopping previous scene because we don't display clip slot stop buttons
        for track in previous_playing_scene.tracks:
            if not track.is_playing or track in self.tracks or isinstance(track, SimpleAudioTailTrack):
                continue

            track.stop(immediate=immediate)

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent)
        seq.add(previous_playing_scene.scene_name.update)
        seq.done()

    def mute_audio_tails(self):
        # type: (Scene) -> None
        for clip in self.clips.audio_tail_clips:
            clip.muted = True

    def duplicate(self):
        # type: (Scene) -> Optional[Sequence]
        if self._scene:  # type: ignore[has-type]
            return self._song.duplicate_scene(self.index)
        return None

    def delete(self):
        # type: (Scene) -> Optional[Sequence]
        if self._scene:  # type: ignore[has-type]
            return self._song.delete_scene(self.index)
        return None

    def split(self):
        # type: (Scene) -> Sequence
        start_window, end_window = SceneWindow.create_from_split(self, self.crop_scroller.current_value)
        seq = Sequence()
        seq.add(self.duplicate)
        seq.add(partial(start_window.apply_to_scene, self))
        seq.add(lambda: end_window.apply_to_scene(SongFacade.selected_scene()))

        return seq.done()

    def crop(self):
        # type: (Scene) -> Sequence
        window = SceneWindow.create_from_crop(self, self.crop_scroller.current_value)
        seq = Sequence()
        seq.add(self.duplicate)
        seq.add(lambda: window.apply_to_scene(SongFacade.selected_scene()))

        return seq.done()

    def fire_to_position(self):
        # type: (Scene) -> Sequence
        self._song.stop_playing()
        self._song.session_automation_record = True
        seq = Sequence()
        # removing click when changing position
        master_volume = SongFacade.master_track().volume
        SongFacade.master_track().volume = 0
        seq.defer()
        # leveraging throttle to disable the next update (that would be 1 / *)
        seq.add(partial(self.scene_name.update, bar_position=self.position_scroller.current_value))
        seq.add(self.fire)
        seq.defer()
        seq.add(partial(self.jump_to_bar, min(self.bar_length - 1, self.position_scroller.current_value)))
        seq.add(partial(setattr, SongFacade.master_track(), "volume", master_volume))
        seq.add(partial(setattr, self._song, "session_record", True))
        return seq.done()

    def jump_to_bar(self, bar_position):
        # type: (Scene, float) -> None
        beat_offset = (bar_position * SongFacade.signature_numerator()) - self.playing_position.position
        self._song.scrub_by(beat_offset)
