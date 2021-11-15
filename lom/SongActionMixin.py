from functools import partial

from typing import TYPE_CHECKING, Optional, Any

from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.lom.device.Device import Device
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import handle_error, arrangement_view_only, session_view_only
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.Song import Song


# noinspection PyTypeHints,PyArgumentList
class SongActionMixin(object):
    def get_data(self, key, default_value=None):
        # type: (Song, str, Any) -> Any
        return self._song.get_data(key, default_value)

    def set_data(self, key, value):
        # type: (Song, str, Any) -> None
        if isinstance(value, AbstractEnum):
            value = value.value
        self._song.set_data(key, value)

    def activate_arrangement(self):
        # type: (Song) -> None
        self.parent.navigationManager.show_arrangement()
        self._song.back_to_arranger = False

    @handle_error
    def reset(self):
        # type: (Song) -> None
        """ stopping immediately """
        self.stop_playing()
        # noinspection PyPropertyAccess
        self._song.current_song_time = 0
        self.stop_all_clips()

    def play(self):
        # type: (Song) -> None
        if self.session_view_active:
            self._play_session()
        else:
            self._play_arrangement()

    @session_view_only
    def _play_session(self, from_beginning=False):
        # type: (Song, bool) -> None
        scene = self.scenes[0] if from_beginning else self.selected_scene
        scene.fire()
        # noinspection PyUnresolvedReferences
        scene.notify_play()

    @arrangement_view_only
    def _play_arrangement(self):
        # type: (Song) -> None
        self.is_playing = True

    def stop_playing(self):
        # type: (Song) -> None
        self._song.stop_playing()

    def stop_all_clips(self, quantized=1):
        # type: (Song, int) -> None
        # noinspection PyTypeChecker
        self._song.stop_all_clips(quantized)

    def bounce_session_to_arrangement(self):
        # type: (Song) -> Sequence
        tempo = self.tempo
        for armed_track in self.armed_tracks:  # type: AbstractTrack
            armed_track.unarm()
        self.tempo = 999
        self.parent.sceneBeatScheduler.clear()

        self.parent.navigationManager.show_arrangement()

        seq = Sequence()
        seq.add(self.system.clear_arrangement)
        seq.add(wait=20)
        seq.add(self.parent.navigationManager.show_session)
        seq.add(self.reset)
        seq.add(partial(setattr, self.song, "record_mode", True))
        seq.add(partial(self._play_session, from_beginning=True), complete_on=self.song.session_end_listener,
                no_timeout=True)
        seq.add(partial(setattr, self.song, "record_mode", False))
        seq.add(self.reset)
        seq.add(partial(setattr, self.song, "tempo", tempo))
        seq.add(self.song.activate_arrangement)
        return seq.done()

    def begin_undo_step(self):
        # type: (Song) -> None
        self._song.begin_undo_step()

    def end_undo_step(self):
        # type: (Song) -> None
        self._song.end_undo_step()

    def undo(self):
        # type: (Song) -> None
        self.metronome = False
        self._song.undo()

    def select_track(self, abstract_track):
        # type: (Song, AbstractTrack) -> Sequence
        if abstract_track.group_track:
            abstract_track.group_track.is_folded = False
        seq = Sequence(silent=True)
        if self.song.selected_track != abstract_track.base_track:
            self._view.selected_track = abstract_track._track
            seq.add(wait=1)
        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (Song, bool) -> None
        if not self.song.selected_track.is_active:
            next(self.song.simple_tracks).select()
        else:
            scroll_values(self.scrollable_tracks, self.current_track, go_next).select()

    def unfocus_all_tracks(self):
        # type: (Song) -> Sequence
        self._unsolo_all_tracks()
        return self.unarm_all_tracks()

    def unarm_all_tracks(self):
        # type: (Song) -> Sequence
        seq = Sequence(silent=True)
        seq.add([t.unarm for t in self.abstract_tracks])
        return seq.done()

    def _unsolo_all_tracks(self, except_current=True):
        # type: (Song, bool) -> None
        for t in self.song.abstract_tracks:
            if t.solo and t != (self.current_track if except_current else None):
                t.solo = False

    def duplicate_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        seq.add(partial(self._song.duplicate_track, index), complete_on=self.parent.songManager.tracks_listener)
        return seq.done()

    def duplicate_scene(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        # seq.add(partial(self._song.duplicate_scene, index))
        seq.add(partial(self._song.duplicate_scene, index), complete_on=self.parent.songManager.tracks_listener)
        return seq.done()

    def scroll_scenes(self, go_next):
        # type: (Song, bool) -> None
        scroll_values(self.scenes, self.selected_scene, go_next).select()

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> Sequence
        seq = Sequence()
        scenes_count = len(self.song.scenes)
        seq.add(lambda: self._song.create_scene(scene_index or scenes_count), complete_on=lambda: len(self.song.scenes) > scenes_count)
        seq.add(wait=1)
        return seq.done()

    def delete_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> Sequence
        seq = Sequence()
        scenes_count = len(self.song.scenes)
        seq.add(lambda: self._song.delete_scene(scene_index), complete_on=lambda: len(self.song.scenes) < scenes_count)
        seq.add(wait=1)
        return seq.done()

    def select_device(self, device):
        # type: (Song, Device) -> Sequence
        seq = Sequence()
        seq.add(partial(self.song.select_track, device.track))
        seq.add(partial(self._view.select_device, device._device))
        seq.add(self.parent.navigationManager.focus_detail)
        return seq.done()

    def tap_tempo(self):
        # type: (Song) -> None
        self._song.tap_tempo()
