from typing import Callable, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.CommandEnum import CommandEnum
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.AbstractTrackList import AbstractTrackList
from protocol0.utils.decorators import api_exposed, api_exposable_class
from protocol0.utils.log import log_ableton
from protocol0.utils.utils import normalize_string


@api_exposable_class
class SearchManager(AbstractControlSurfaceComponent):
    @api_exposed
    def test(self):
        # type: () -> None
        log_ableton("test API called successful")

    @api_exposed
    def execute_command(self, command):
        # type: (str) -> None
        if CommandEnum.get_from_value(command):
            self._execute_command(command=command)
        else:
            self.search_track(search=command)

    def _execute_command(self, command):
        if command == CommandEnum.FOLD.name:
            AbstractTrackList(self.song.abstract_tracks).toggle_fold()

    def search_track(self, search):
        # type: (str) -> None
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
            if criteria(track, search):
                return track

        return None
