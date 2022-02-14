from functools import partial
from math import floor

from typing import TYPE_CHECKING, Optional, cast

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.shared.decorators import throttle
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
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
            self._fire_next_scene()

    def _fire_next_scene(self):
        # type: (Scene) -> None
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

    def fire_and_move_position(self):
        # type: (Scene) -> Sequence
        self._song.stop_playing()
        seq = Sequence()

        from protocol0.domain.lom.scene.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION >= self.bar_length:
            Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = 0

        # removing click when changing position
        master_volume = SongFacade.master_track().volume
        SongFacade.master_track().volume = 0
        seq.add(wait=1)
        # leveraging throttle to disable the next update (that would be 1 / *)
        seq.add(partial(self.scene_name.update, bar_position=Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION))
        seq.add(self.fire)
        seq.add(partial(self.jump_to_bar, Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION))
        seq.add(self._song.stop_playing)
        seq.add(partial(setattr, SongFacade.master_track(), "volume", master_volume))
        seq.add(wait=1)
        seq.add(self._song.continue_playing)
        return seq.done()

    def pre_fire(self):
        # type: (Scene) -> Sequence
        self.fire()
        self._song.stop_playing()
        seq = Sequence()
        seq.add(wait=2)
        return seq.done()

    def _stop_previous_scene(self, previous_playing_scene, immediate=False):
        # type: (Scene, Scene, bool) -> None
        from protocol0.domain.lom.scene.Scene import Scene

        if previous_playing_scene == SongFacade.looping_scene():
            Scene.LOOPING_SCENE = None

        # manually stopping previous scene because we don't display clip slot stop buttons
        for track in previous_playing_scene.tracks:
            if not track.is_playing or track in self.tracks or isinstance(track, SimpleAudioTailTrack):
                continue

            track.stop(immediate=immediate)

        Scheduler.wait_beats(1, partial(previous_playing_scene.scene_name.update, display_bar_count=False))

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

    def toggle_loop(self):
        # type: (Scene) -> None
        """ for a scene solo means looped """
        from protocol0.domain.lom.scene.Scene import Scene

        if self != SongFacade.looping_scene():  # solo activation
            previous_looping_scene = SongFacade.looping_scene()
            Scene.LOOPING_SCENE = self
            if self != SongFacade.playing_scene():
                self.fire()
            if previous_looping_scene and previous_looping_scene != self:
                previous_looping_scene.scene_name.update()
        else:  # solo inactivation
            Scene.LOOPING_SCENE = None

        self.scene_name.update()

    def split(self, bar_length):
        # type: (Scene, int) -> Sequence
        if bar_length == 0:
            raise Protocol0Warning("Please select a bar length")

        StatusBar.show_message("Splitting scene one %d bar(s)" % bar_length)
        length = bar_length * SongFacade.signature_numerator()
        seq = Sequence()
        seq.add(self.duplicate)
        seq.add(partial(self._crop_clips, 0, length))
        seq.add(lambda: self._song.selected_scene._crop_clips(length, self.length))
        for track in SongFacade.external_synth_tracks():
            if track.audio_tail_track and track.audio_tail_track.clip_slots[self.index]:
                seq.add([track.audio_tail_track.clip_slots[self.index].clip.delete])
        return seq.done()

    def _crop_clips(self, start, end):
        # type: (Scene, float, float) -> None
        for clip in self.clips:
            if start == 0 and isinstance(clip, AudioTailClip):
                clip.delete()
                return

            clip.loop.start = start
            clip.loop.end = end

    @throttle(wait_time=10)
    def scroll_position(self, go_next):
        # type: (Scene, bool) -> None
        from protocol0.domain.lom.scene.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE != self:
            Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = 0
            Scene.LAST_MANUALLY_STARTED_SCENE = self
        scene_position = Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION

        if self.has_playing_clips:
            bar_position = self.playing_position * SongFacade.signature_numerator()
            rounded_bar_position = floor(bar_position) if go_next else round(bar_position)
            scene_position = int(scroll_values(range(0, self.bar_length), rounded_bar_position, go_next=go_next))
            self.jump_to_bar(scene_position)
        else:
            scene_position = scroll_values(range(0, self.bar_length), scene_position, go_next=go_next)

        Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = scene_position
        self.scene_name.update(bar_position=scene_position)

    def jump_to_bar(self, bar_position):
        # type: (Scene, float) -> None
        beat_offset = (bar_position * SongFacade.signature_numerator()) - self.playing_position
        self._song.scrub_by(beat_offset)
