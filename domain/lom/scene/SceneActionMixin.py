from functools import partial

from typing import TYPE_CHECKING, Optional, cast

from protocol0.domain.lom.scene.SceneWindow import SceneWindow
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
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
        if self.is_recording:
            return
        # if it is the last bar
        if self.current_bar == self.bar_length - 1:
            self._play_audio_tails()
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can loose current parameter focus)

    def fire(self):
        # type: (Scene) -> None
        # handles click sound when the previous scene plays shortly
        if SongFacade.playing_scene() and SongFacade.playing_scene() != self:
            self._stop_previous_scene(SongFacade.playing_scene())

        from protocol0.domain.lom.scene.Scene import Scene
        Scene.PLAYING_SCENE = self

        self._scene.fire()

    def pre_fire(self):
        # type: (Scene) -> Sequence
        self.fire()
        self._song.stop_playing()
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

        seq = Sequence()
        seq.add(wait_for_event=BarChangedEvent)
        seq.add(previous_playing_scene.scene_name.update)
        seq.done()

    def _play_audio_tails(self):
        # type: (Scene) -> None
        for clip in self.audio_tail_clips:
            abstract_track = cast(ExternalSynthTrack, clip.track.abstract_track)
            if abstract_track.audio_track.clip_slots[clip.index].clip.muted:
                continue

            clip.play_and_mute()

    def mute_audio_tails(self):
        # type: (Scene) -> None
        for clip in self.audio_tail_clips:
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
        start_window, end_window = SceneWindow.create_from_split(self)

        seq = Sequence()
        seq.add(self.duplicate)

        # crop first half
        seq.add(partial(start_window.apply_to_scene, self))
        # crop 2nd half
        seq.add(lambda: end_window.apply_to_scene(SongFacade.selected_scene()))

        return seq.done()

    def crop(self):
        # type: (Scene) -> Sequence
        window = SceneWindow.create_from_crop(self)
        seq = Sequence()
        seq.add(self.duplicate)
        seq.add(lambda: window.apply_to_scene(SongFacade.selected_scene()))

        return seq.done()

    def fire_to_position(self):
        # type: (Scene) -> Sequence
        self._song.stop_playing()
        seq = Sequence()
        # removing click when changing position
        master_volume = SongFacade.master_track().volume
        SongFacade.master_track().volume = 0
        seq.add(wait=1)
        # leveraging throttle to disable the next update (that would be 1 / *)
        seq.add(partial(self.scene_name.update, bar_position=self.position_scroller.current_value))
        seq.add(self.fire)
        seq.add(wait=1)
        seq.add(partial(self.jump_to_bar, min(self.bar_length - 1, self.position_scroller.current_value)))
        seq.add(partial(setattr, SongFacade.master_track(), "volume", master_volume))
        return seq.done()

    def jump_to_bar(self, bar_position):
        # type: (Scene, float) -> None
        beat_offset = (bar_position * SongFacade.signature_numerator()) - self.playing_position
        self._song.scrub_by(beat_offset)
