from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


# noinspection PyTypeHints
class SongActionMixin(object):
    def action_next(self, go_next):
        # type: ("Song", bool) -> str
        selected_track_index = self.selected_track.index if self.selected_track else 0
        next_track = self.get_next_track_by_index(selected_track_index, bool(go_next))
        action_list = "; {0}/sel".format(next_track.index)
        self.view.selected_track = next_track.track  # mostly to ease testing
        return action_list

    @property
    def action_restart(self):
        # type: ("Song") -> str
        action_list = "".join([track.action_restart for track in self.tracks])
        return "setplay on" + action_list if action_list else ""

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
