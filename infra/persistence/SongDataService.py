from typing import Optional, Callable

from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.SelectedRecordingBarLengthUpdatedEvent import \
    SelectedRecordingBarLengthUpdatedEvent
from protocol0.infra.persistence.SongDataEnum import SongDataEnum
from protocol0.infra.persistence.SongDataError import SongDataError
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class SongDataService(object):
    DEBUG = False

    def __init__(self, get_data, set_data):
        # type: (Callable, Callable) -> None

        self._set_data = set_data
        self._get_data = get_data

        self._selected_scene_index = None  # type: Optional[int]
        self._selected_track_index = None  # type: Optional[int]

        DomainEventBus.subscribe(SongInitializedEvent, lambda _: self._restore())
        DomainEventBus.subscribe(SelectedRecordingBarLengthUpdatedEvent, lambda _: self.save())

    def save(self):
        # type: () -> None
        # can happen on record e.g.
        if SongFacade.selected_scene():
            self._set_data(SongDataEnum.SELECTED_SCENE_INDEX.value, SongFacade.selected_scene().index)
        if SongFacade.selected_track():
            self._set_data(SongDataEnum.SELECTED_TRACK_INDEX.value, SongFacade.selected_track().index)

    def _restore(self):
        # type: () -> None
        try:
            self._selected_scene_index = self._get_data(SongDataEnum.SELECTED_SCENE_INDEX.value, None)
            self._selected_track_index = self._get_data(SongDataEnum.SELECTED_TRACK_INDEX.value, None)

            self._restore_set_state()
        except SongDataError as e:
            Logger.log_error(str(e))
            raise Protocol0Warning("Inconsistent song data please save the set")

    def _restore_set_state(self):
        # type: () -> None
        if self._selected_scene_index is not None and self._selected_scene_index < len(
                SongFacade.scenes()):
            selected_scene = SongFacade.scenes()[self._selected_scene_index]
            selected_scene.select()
        if self._selected_track_index is not None and self._selected_track_index < len(
                list(SongFacade.all_simple_tracks())):
            selected_track = list(SongFacade.all_simple_tracks())[self._selected_track_index]
            selected_track.select()
