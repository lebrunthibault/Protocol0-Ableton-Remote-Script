from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.enums.FoldActionEnum import FoldActionEnum
from protocol0.lom.Scene import Scene
from protocol0.lom.device.Device import Device
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.AbstractTrackList import AbstractTrackList
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import handle_error
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.Song import Song


# noinspection PyTypeHints,PyArgumentList
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
        if self.song.selected_track == self.song.master_track:
            self.song.select_track(next(self.song.abstract_tracks))

        for scene in reversed(self.song.scenes):
            if scene.length == 0 and len(self.song.scenes):
                self.song.delete_scene(scene=scene)
                self.song.scenes.remove(scene)

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

    def select_track(self, abstract_track, fold_set=False):
        # type: (Song, AbstractTrack, bool) -> Optional[Sequence]
        seq = Sequence(silent=True)
        if self.song.selected_track != abstract_track.base_track:
            seq.add(partial(setattr, self._view, "selected_track", abstract_track._track), wait=1)
        if fold_set:
            if abstract_track.is_foldable:
                abstract_track.is_folded = False
            seq.add(partial(AbstractTrackList(self.song.abstract_tracks).toggle_fold,
                            fold_action=FoldActionEnum.FOLD_ALL_EXCEPT_CURRENT))
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
        try:
            self._song.delete_scene(scene.index)
        except RuntimeError as e:
            self.parent.log_warning("Error while deleting %s: %s" % (scene, e))

    def select_device(self, device):
        # type: (Song, Device) -> Sequence
        seq = Sequence()
        seq.add(partial(self.song.select_track, device.track))
        seq.add(partial(self._view.select_device, device._device))
        seq.add(self.parent.navigationManager.focus_detail)
        return seq.done()
