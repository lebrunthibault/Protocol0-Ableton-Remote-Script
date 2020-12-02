from typing import TYPE_CHECKING, Optional, Any

from a_protocol_0.lom.track.SimpleTrack import SimpleTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def scroll_tracks(self, go_next):
        # type: (Song, bool) -> None
        selected_track_index = self.selected_track.index if self.selected_track else 0
        self.get_next_track_by_index(selected_track_index, go_next).is_selected = True

    def unfocus_other_tracks(self):
        self._unarm_other_tracks()
        self._unsolo_other_tracks()

    def _unarm_other_tracks(self):
        # type: (Song) -> None
        [t.action_unarm() for t in self.simple_tracks if t.arm and t != self.current_track]
        [g_track.action_unarm() for g_track in self.g_tracks if g_track.arm and g_track != self.current_track]

    def _unsolo_other_tracks(self):
        # type: (Song) -> None
        [setattr(t, "solo", False) for t in self.song.solo_tracks if t.solo and t != self.current_track.base_track]

    def get_next_track_by_index(self, index, go_next):
        # type: (Song, int, bool) -> SimpleTrack
        tracks = self.top_tracks if go_next else list(reversed(self.top_tracks))

        if len(tracks) == 0:
            raise Exception("No tracks in this set")

        for track in tracks:
            if go_next and track.index > index:
                return track
            elif not go_next and track.index < index:
                return track

        return tracks[0]

    def stop_all_clips(self):
        # type: (Song) -> None
        self._song.stop_all_clips()

    def select_device(self, device):
        # type: (Song, Any) -> None
        self.view.select_device(device)

    def undo(self):
        # type: (Song) -> None
        self._song.undo()

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> None
        self._song.view.selected_scene = self._song.create_scene(scene_index or len(self.song.scenes))

