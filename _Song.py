from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._log import log_ableton


class Song:
    def __init__(self, song):
        # type: (_) -> None
        self._song = song
        # tracks = [track for track in song.tracks if
        #           track != song.master_track and track not in song.return_tracks]

        log_ableton(song.tracks[0])
        self.tracks = [Track(track, i + 1) for i, track in enumerate(list(song.tracks))]
        # self.tracks = [Track(track, i + 1) for i, track in enumerate(tracks)]
    #
    # @property
    # def tracks_visible(self):
    #     return [track for track in self.tracks if track.is_visible]
