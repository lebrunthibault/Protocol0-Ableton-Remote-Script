from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.decorators import api_exposed, api_exposable_class
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import normalize_string
from typing import Callable, Optional


@api_exposable_class
class SearchManager(AbstractControlSurfaceComponent):
    @api_exposed
    def test(self):
        # type: () -> None
        log_ableton("test API called successful")

    @api_exposed
    def search_track(self, search):
        # type: (str) -> None
        self.parent.log_dev(search)
        if len(search) < 3:
            return

        search = search.lower().strip()

        criterias = [
            lambda track, search: normalize_string(track.name).startswith(search),
            lambda track, search: search in normalize_string(track.name),
            lambda track, search: track.instrument and search in normalize_string(track.instrument.name),
        ]

        for criteria in criterias:
            matching_track = self._search_by_criteria(search, criteria)
            if matching_track:
                self.parent.log_info("Found track %s for search: %s" % (matching_track.name.lower(), search.lower()))
                self.song.select_track(matching_track, fold_set=True)
                return

        self.parent.log_info("Didn't find track for search: %s" % search.lower())
        return None

    def _search_by_criteria(self, search, criteria):
        # type: (str, Callable) -> Optional[AbstractTrack]
        for track in self.song.abstract_tracks:
            self.parent.log_dev(track.name)
            if criteria(track, search):
                return track

        return None
