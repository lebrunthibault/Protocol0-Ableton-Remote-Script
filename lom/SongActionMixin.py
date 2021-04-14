from functools import partial

from typing import TYPE_CHECKING, Optional

from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import scroll_values

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def select_track(self, selected_track):
        # type: (Song, AbstractTrack, bool) -> Sequence
        if self.song.selected_track == selected_track.base_track:
            return
        seq = Sequence(silent=True)
        seq.add(partial(setattr, self._view, "selected_track", selected_track._track), wait=1)
        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (Song, bool) -> None
        base_track = self.selected_track if self.selected_track.is_scrollable else self.current_track.base_track
        track_to_select = scroll_values(self.scrollable_tracks, base_track, go_next)  # type: SimpleTrack
        if track_to_select:
            track_to_select.select()

    def unfocus_all_tracks(self):
        # type: (Song, bool) -> None
        self.unsolo_all_tracks()
        return self.unarm_all_tracks()

    def unarm_all_tracks(self):
        # type: (Song, bool) -> None
        seq = Sequence(silent=True)
        seq.add([t.unarm() for t in self.abstract_tracks if t.is_armed])
        return seq.done()

    def unsolo_all_tracks(self, except_current=True):
        # type: (Song, bool) -> None
        [setattr(t, "solo", False) for t in self.song.abstract_tracks if
         t.solo and t != (self.current_track if except_current else None)]

    def fold_all_tracks(self):
        # type: (Song, bool) -> None
        # 1st we fold all except current
        other_group_tracks = [track for track in self.song.root_tracks if
                              track.is_foldable and track != self.current_track.base_track]
        if len(filter(None, [not track.is_folded for track in other_group_tracks])):
            [setattr(track, "is_folded", True) for track in other_group_tracks]
        else:
            self.current_track.is_folded = True

    def reset(self):
        # type: (Song) -> None
        self.stop_all_clips(0)
        self.stop_playing()
        self._song.current_song_time = 0
        [track.reset_track() for track in self.abstract_tracks]

    def play_stop(self):
        # type: (Song) -> None
        if not self.is_playing:
            self.selected_scene.fire()
        else:
            self.stop_all_clips()

    def stop_playing(self):
        # type: (Song) -> None
        self._song.stop_playing()

    def stop_all_clips(self, quantized=1):
        # type: (Song, int) -> None
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

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> Sequence
        seq = Sequence()
        seq.add(lambda: self._song.create_scene(scene_index or len(self.song.scenes)), wait=1)
        return seq.done()

    def select_device(self, device):
        # type: (Song, Device) -> None
        if device:
            self._view.select_device(device._device)
