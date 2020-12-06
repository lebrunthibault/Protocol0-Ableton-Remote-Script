from typing import TYPE_CHECKING, Optional

from a_protocol_0.lom.track.SimpleTrack import SimpleTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def select_track(self, selected_track):
        # type: (Song, SimpleTrack) -> None
        self._view.selected_track = selected_track._track

    def unfocus_all_tracks(self):
        # type: (Song) -> None
        self.parent.log_debug("unfocus all tracks")
        self._unarm_all_tracks()
        self._unsolo_all_tracks()

    def _unarm_all_tracks(self):
        # type: (Song) -> None
        [t.action_unarm() for t in self.external_synth_tracks if t.arm]
        [t.action_unarm() for t in self.tracks if t.arm]

    def _unsolo_all_tracks(self):
        # type: (Song) -> None
        [setattr(t, "solo", False) for t in self.song.solo_tracks if t.solo]

    def stop(self):
        # type: (Song) -> None
        self.stop_all_clips(0)
        self.stop_playing()
        self._song.current_song_time = 0

    def stop_playing(self):
        # type: (Song) -> None
        self._song.stop_playing()

    def stop_all_clips(self, quantized=1):
        # type: (Song, int) -> None
        self._song.stop_all_clips(quantized)

    def undo(self):
        # type: (Song) -> None
        self._song.undo()

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> None
        self.song._view.selected_scene = self._song.create_scene(scene_index or len(self.song.scenes))

