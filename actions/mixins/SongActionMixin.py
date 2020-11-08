from typing import TYPE_CHECKING, Optional

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def scroll_tracks(self, go_next):
        # type: ("Song", bool) -> None
        selected_track_index = self.selected_track.index if self.selected_track else 0
        next_track = self.get_next_track_by_index(selected_track_index, bool(go_next))
        next_track.is_selected = True

    def restart_set(self):
        # type: ("Song") -> None
        [track.restart() for track in self.tracks]

    def get_next_track_by_index(self, index, go_next):
        # type: ("Song", int, bool) -> SimpleTrack
        tracks = self.top_tracks if go_next else list(reversed(self.top_tracks))

        if len(tracks) == 0:
            raise Exception("No tracks in this set")

        for track in tracks:
            if go_next and track.index > index:
                return track
            elif not go_next and track.index < index:
                return track

        return tracks[0]

    def undo(self):
        # type: ("Song") -> None
        self._song.undo()

    def create_scene(self, scene_index=None):
        # type: ("Song", Optional[int]) -> None
        self._song.view.selected_scene = self._song.create_scene(scene_index or self.scene_count)

    def rename_all_clips(self):
        # type: ("Song") -> None
        [track.restart() for track in self.tracks]

