from protocol0.enums.FoldActionEnum import FoldActionEnum
from protocol0.lom.Scene import Scene
from protocol0.lom.device.Device import Device
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.AbstractTrackList import AbstractTrackList
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import handle_error
from protocol0.utils.utils import scroll_values
from functools import partial
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from protocol0.lom.Song import Song


class SongActionMixin(object):
    @handle_error
    def reset(self, reset_tracks=True):
        # type: (Song, bool) -> None
        """ stopping immediately """
        self.stop_playing()
        self._song.current_song_time = 0
        self.stop_all_clips()
        if reset_tracks:
            for track in self.abstract_tracks:
                track.reset_track()

    def play_stop(self):
        # type: (Song) -> None
        if not self.is_playing:
            self.selected_scene.fire()
        else:
            self.reset(False)

    def stop_playing(self):
        # type: (Song) -> None
        self._song.stop_playing()

    def stop_all_clips(self, quantized=1):
        # type: (Song, int) -> None
        # noinspection PyTypeChecker
        self._song.stop_all_clips(quantized)

    def begin_undo_step(self):
        # type: (Song) -> None
        self._song.begin_undo_step()

    def end_undo_step(self):
        # type: (Song) -> None
        self._song.end_undo_step()

    def undo(self):
        # type: (Song) -> None
        self._song.undo()

    def select_track(self, selected_track, fold_set=False):
        # type: (Song, AbstractTrack, bool) -> Optional[Sequence]
        if self.song.selected_track == selected_track.base_track:
            return None
        if fold_set:
            AbstractTrackList(self.song.abstract_tracks).toggle_fold(fold_action=FoldActionEnum.FOLD_ALL)
        group_track = selected_track.group_track
        while group_track:
            group_track.is_folded = False
            group_track = group_track.group_track
        seq = Sequence(silent=True)
        seq.add(partial(setattr, self._view, "selected_track", selected_track._track), wait=1)
        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (Song, bool) -> None
        if not self.song.selected_track.is_active:
            next(self.song.simple_tracks).select()
        else:
            scroll_values(self.scrollable_tracks, self.current_track, go_next).select()

    def unfocus_all_tracks(self):
        # type: (Song) -> Sequence
        self.unsolo_all_tracks()
        return self.unarm_all_tracks()

    def unarm_all_tracks(self):
        # type: (Song) -> Sequence
        seq = Sequence(silent=True)
        seq.add([t.unarm for t in self.abstract_tracks if t.is_armed])
        return seq.done()

    def unsolo_all_tracks(self, except_current=True):
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
        seq.add(lambda: self._song.create_scene(scene_index or len(self.song.scenes)), wait=1)
        return seq.done()

    def delete_scene(self, scene):
        # type: (Song, Scene) -> None
        self._song.delete_scene(scene.index)

    def select_device(self, device):
        # type: (Song, Device) -> None
        if device:
            self.parent.navigationManager.focus_detail()
            self._view.select_device(device._device)
