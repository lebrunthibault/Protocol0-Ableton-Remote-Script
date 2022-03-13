from typing import List

from protocol0.application.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.track_list.AbstractTrackList import AbstractTrackList
from protocol0.domain.lom.track.track_list.FoldActionEnum import FoldActionEnum
from protocol0.domain.shared.utils import normalize_string
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class KeywordSearchService(object):
    LAST_SEARCH = None  # type: TrackSearchKeywordEnum

    def search_track(self, keyword_enum):
        # type: (TrackSearchKeywordEnum) -> None
        self.LAST_SEARCH = keyword_enum

        if keyword_enum == TrackSearchKeywordEnum.MASTER:
            if SongFacade.master_track():
                SongFacade.master_track().select()
            return

        search = keyword_enum.search_value

        matching_tracks = []
        for track in SongFacade.abstract_tracks():
            if self._check_search_matches_track(search=search, track=track):
                matching_tracks.append(track)

        if len(matching_tracks) == 0:
            Logger.info("Didn't find track for search: %s" % search.lower())
            return

        index = 0
        if SongFacade.current_track() in matching_tracks:
            index = (matching_tracks.index(SongFacade.current_track()) + 1) % len(matching_tracks)

        matching_track = matching_tracks[index]

        Logger.info("Selecting track %s" % matching_track)
        matching_track.select()
        if matching_track.is_foldable:
            matching_track.is_folded = False
        AbstractTrackList(SongFacade.abstract_tracks()).toggle_fold(fold_action=FoldActionEnum.FOLD_ALL_EXCEPT_CURRENT)

    def _check_search_matches_track(self, search, track):
        # type: (str, AbstractTrack) -> bool
        for track_keyword in self._get_track_keywords(track):
            if search in normalize_string(track_keyword).split(" "):
                Logger.info("found match for search %s in track %s (track keyword matched: %s)" %
                            (search, track, track_keyword))
                return True

        return False

    def _get_track_keywords(self, track):
        # type: (AbstractTrack) -> List[str]
        keywords = [track.name]
        if track.instrument:
            keywords += [track.instrument.name]
            if track.instrument.selected_preset:
                keywords += [track.instrument.selected_preset.name]
        unique_keywords = list(set(" ".join(keywords).lower().split(" ")))
        return [kw for kw in unique_keywords if len(kw) >= 3]
