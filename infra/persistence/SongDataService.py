from typing import Callable

from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.persistence.SongDataEnum import SongDataEnum
from protocol0.shared.SongFacade import SongFacade


class SongDataElement(object):
    def __init__(self, get_value):
        # type: (Callable) -> None
        self.get_value = get_value
        self.saved_value = None


class SongDataService(object):
    """Service handling data storage in the set"""
    _DEBUG = False

    def __init__(self, get_data, set_data, scene_component):
        # type: (Callable, Callable, SceneComponent) -> None

        self._set_data = set_data
        self._get_data = get_data
        self._scene_component = scene_component

        self._elements = {
            SongDataEnum.SELECTED_SCENE_INDEX: SongDataElement(
                lambda: SongFacade.selected_scene().index
            ),
            SongDataEnum.SELECTED_TRACK_INDEX: SongDataElement(
                lambda: SongFacade.selected_track().index
            ),
        }

        self._restore()
        DomainEventBus.subscribe(SceneFiredEvent, lambda _: self.save())

    def save(self):
        # type: () -> None
        """Save watched elements in the set data"""
        for enum, element in self._elements.items():
            self._set_data(enum.value, element.get_value())

    def _restore(self):
        # type: () -> None
        """Restore data from set data to script"""
        for enum, element in self._elements.items():
            element.saved_value = self._get_data(enum.value, None)

        # time for script to be initialized
        Scheduler.defer(self._restore_set_state)

    def _restore_set_state(self):
        # type: () -> None
        selected_scene_index = self._elements.get(SongDataEnum.SELECTED_SCENE_INDEX).saved_value
        if selected_scene_index is not None and selected_scene_index < len(SongFacade.scenes()):
            selected_scene = SongFacade.scenes()[selected_scene_index]
            self._scene_component.select_scene(selected_scene)

        selected_track_index = self._elements.get(SongDataEnum.SELECTED_TRACK_INDEX).saved_value
        if selected_track_index is not None and selected_track_index < len(
            list(SongFacade.all_simple_tracks())
        ):
            selected_track = list(SongFacade.all_simple_tracks())[selected_track_index]
            selected_track.select()
