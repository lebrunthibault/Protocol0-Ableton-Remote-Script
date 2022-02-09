from typing import Optional, Callable

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenesService import SongScenesService
from protocol0.domain.lom.scene.SelectedDuplicateSceneBarLengthUpdatedEvent import \
    SelectedDuplicateSceneBarLengthUpdatedEvent
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.SongResetedEvent import SongResetedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordingBarLengthEnum import RecordingBarLengthEnum
from protocol0.domain.track_recorder.SelectedRecordingBarLengthUpdatedEvent import \
    SelectedRecordingBarLengthUpdatedEvent
from protocol0.domain.track_recorder.track_recorder_service import TrackRecorderService
from protocol0.infra.persistence.SongDataEnum import SongDataEnum
from protocol0.infra.persistence.SongDataError import SongDataError
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SongDataService(object):
    DEBUG = False

    def __init__(self, get_data, set_data, track_recorder_service, song_scenes_service):
        # type: (Callable, Callable, TrackRecorderService, SongScenesService) -> None

        self._set_data = set_data
        self._get_data = get_data
        self._track_recorder_service = track_recorder_service
        self._song_scenes_service = song_scenes_service

        self._selected_scene_index = None  # type: Optional[int]
        self._selected_track_index = None  # type: Optional[int]
        self._last_manually_started_scene_index = None  # type: Optional[int]
        self._last_manually_started_scene_bar_position = 0

        DomainEventBus.subscribe(SongResetedEvent, lambda _: self.save())
        DomainEventBus.subscribe(SongInitializedEvent, lambda _: self._restore())
        DomainEventBus.subscribe(SelectedRecordingBarLengthUpdatedEvent, lambda _: self.save())
        DomainEventBus.subscribe(SelectedDuplicateSceneBarLengthUpdatedEvent, lambda _: self.save())

        # self._restore()

    def save(self):
        # type: () -> None
        self._set_data(SongDataEnum.SELECTED_RECORDING_BAR_LENGTH.value, self._track_recorder_service.selected_recording_bar_length.bar_length_value)
        self._set_data(SongDataEnum.SELECTED_DUPLICATE_SCENE_BAR_LENGTH.value, self._song_scenes_service.selected_duplicate_scene_bar_length)

        # can happen on record e.g.
        if SongFacade.selected_scene():
            self._set_data(SongDataEnum.SELECTED_SCENE_INDEX.value, SongFacade.selected_scene().index)
        if SongFacade.selected_track():
            self._set_data(SongDataEnum.SELECTED_TRACK_INDEX.value, SongFacade.selected_track().index)

        from protocol0.domain.lom.scene.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE:
            self._set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.value, Scene.LAST_MANUALLY_STARTED_SCENE.index)
            self._set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.value, Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION)

    def _restore(self):
        # type: () -> None
        try:
            self._track_recorder_service.selected_recording_bar_length = RecordingBarLengthEnum.from_value(self._get_data(SongDataEnum.SELECTED_RECORDING_BAR_LENGTH.value, 4))
            self._song_scenes_service.selected_duplicate_scene_bar_length = RecordingBarLengthEnum.from_value(self._get_data(SongDataEnum.SELECTED_RECORDING_BAR_LENGTH.value, 4))

            self._selected_scene_index = self._get_data(SongDataEnum.SELECTED_SCENE_INDEX.value, None)
            self._selected_track_index = self._get_data(SongDataEnum.SELECTED_TRACK_INDEX.value, None)
            self._last_manually_started_scene_index = self._get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.value, None)
            self._last_manually_started_scene_bar_position = self._get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.value, None)

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
        if self._last_manually_started_scene_index is not None and self._last_manually_started_scene_index < len(
                list(SongFacade.scenes())):
            scene = SongFacade.scenes()[self._last_manually_started_scene_index]
            if not self._last_manually_started_scene_bar_position or self._last_manually_started_scene_bar_position < scene.bar_length:
                Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = self._last_manually_started_scene_bar_position
            Scene.LAST_MANUALLY_STARTED_SCENE = scene
