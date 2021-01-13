from functools import partial

from typing import TYPE_CHECKING, Optional

import Live

from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def select_track(self, selected_track):
        # type: (Song, AbstractTrack, bool) -> Sequence
        seq = Sequence()
        seq.add(partial(setattr, self._view, "selected_track", selected_track.base_track._track),
                do_if=lambda: selected_track != self.song.selected_track)
        seq.add(wait=1)
        return seq.done()

    def unfocus_all_tracks(self, except_current=True):
        # type: (Song, bool) -> None
        self.unarm_all_tracks()
        self.unsolo_all_tracks()

    def unarm_all_tracks(self, except_current=True):
        # type: (Song, bool) -> None
        [t.action_unarm() for t in self.abstract_tracks if
         t.arm and t != (self.current_track if except_current else None)]

    def unsolo_all_tracks(self, except_current=True):
        # type: (Song, bool) -> None
        [setattr(t, "solo", False) for t in self.song.abstract_tracks if
         t.solo and t != (self.current_track if except_current else None)]

    @defer
    def reset(self):
        # type: (Song) -> None
        if self._song.current_song_time == 0 and not self._song.is_playing and self._song.session_record_status == Live.Song.SessionRecordStatus.off:
            return
        self.stop_all_clips(0)
        self.stop_playing()
        self._song.current_song_time = 0
        [track.reset_track() for track in self.tracks]
        [track.reset_track() for track in self.abstract_group_tracks]

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
        # type: (Song, Optional[int]) -> None
        self.song._view.selected_scene = self._song.create_scene(scene_index or len(self.song.scenes))

    def select_device(self, device):
        # type: (Song, Device) -> None
        if device:
            self._view.select_device(device._device)
