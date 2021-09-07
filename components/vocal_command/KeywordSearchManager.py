from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.utils.utils import normalize_string


class KeywordSearchManager(AbstractControlSurfaceComponent):
    LAST_SEARCH = None  # type: TrackSearchKeywordEnum

    def search_track(self, keyword_enum):
        # type: (TrackSearchKeywordEnum) -> None
        self.LAST_SEARCH = keyword_enum

        if keyword_enum == TrackSearchKeywordEnum.MASTER:
            self.song.master_track.select()
            return

        search = keyword_enum.value.lower().strip()

        matching_tracks = []
        for track in self.song.abstract_tracks:
            if self._check_search_matches_track(search=search, track=track):
                matching_tracks.append(track)

        if len(matching_tracks) == 0:
            self.parent.log_info("Didn't find track for search: %s" % search.lower())
            return

        index = 0
        if self.song.current_track in matching_tracks:
            index = (matching_tracks.index(self.song.current_track) + 1) % len(matching_tracks)

        matching_track = matching_tracks[index]

        self.parent.log_info("Selecting track %s" % matching_track)
        self.song.select_track(matching_track, fold_set=True)

    def _check_search_matches_track(self, search, track):
        # type: (str, AbstractTrack) -> bool
        for track_keyword in track.search_keywords:
            if search in normalize_string(track_keyword).split(" "):
                self.parent.log_info("found match for search %s in track %s (track keyword matched: %s)" %
                                     (search, track, track_keyword))
                return True

        return False
