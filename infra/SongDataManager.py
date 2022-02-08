import json
from pydoc import classname

from typing import Optional, Type, Callable, Any

from protocol0.domain.enums.AbstractEnum import AbstractEnum
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.song.SongDataEnum import SongDataEnum
from protocol0.domain.lom.song.SongDataError import SongDataError
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.SongResetedEvent import SongResetedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.SongDataManagerInterface import SongDataManagerInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils import class_attributes
from protocol0.shared.InterfaceState import InterfaceState
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SongDataManager(SongDataManagerInterface):
    DEBUG = False

    def __init__(self, get_data, set_data):
        # type: (Callable, Callable) -> None
        DomainEventBus.subscribe(SongResetedEvent, lambda _: self.save())
        DomainEventBus.subscribe(SongInitializedEvent, lambda _: self._restore_set_state())

        self.__set_data = set_data
        self._get_data = get_data

        self._selected_scene_index = None  # type: Optional[int]
        self._selected_track_index = None  # type: Optional[int]
        self._last_manually_started_scene_index = None  # type: Optional[int]
        self._last_manually_started_scene_bar_position = 0

        self._restore_data()

    def _set_data(self, key, value):
        # type: (str, Any) -> None
        if isinstance(value, AbstractEnum):
            value = value.value
            self.__set_data(key, value)

    def save(self):
        # type: () -> None
        self._set_data(classname(InterfaceState, ""), class_attributes(InterfaceState))

        # can happen on record e.g.
        if SongFacade.selected_scene():
            self._set_data(SongDataEnum.SELECTED_SCENE_INDEX.name, SongFacade.selected_scene().index)
        if SongFacade.selected_track():
            self._set_data(SongDataEnum.SELECTED_TRACK_INDEX.name, SongFacade.selected_track().index)

        from protocol0.domain.lom.scene.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE:
            self._set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.name, Scene.LAST_MANUALLY_STARTED_SCENE.index)
            self._set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.name, Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION)

    def _restore_set_state(self):
        # type: () -> None
        self._restore_data()
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

    def _restore_data(self):
        # type: () -> None
        try:
            self._restore_synchronizable_class_data(InterfaceState)

            self._selected_scene_index = self._get_data(SongDataEnum.SELECTED_SCENE_INDEX.name, None)
            self._selected_track_index = self._get_data(SongDataEnum.SELECTED_TRACK_INDEX.name, None)
            self._last_manually_started_scene_index = self._get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.name, None)
            self._last_manually_started_scene_bar_position = self._get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.name, None)
        except SongDataError as e:
            Logger.log_error(str(e))
            Logger.log_info("setting %s song data to {}")
            self.clear()
            raise Protocol0Warning("Inconsistent song data please save the set")

    def _restore_synchronizable_class_data(self, cls):
        # type: (Type) -> None
        cls_fqdn = classname(cls, "")
        class_data = self._get_data(cls_fqdn, {})
        if self.DEBUG:
            Logger.log_info("song data of %s: %s" % (cls_fqdn, json.dumps(class_data, indent=4, sort_keys=True)))
        if not isinstance(class_data, dict):
            raise SongDataError("%s song data : expected dict, got %s" % (cls_fqdn, class_data))

        for key, value in class_data.items():
            if AbstractEnum.is_json_enum(value):
                try:
                    value = AbstractEnum.from_json_dict(value)
                except Protocol0Error as e:
                    raise SongDataError(e)
            if not hasattr(cls, key):
                Logger.log_warning("Invalid song data, attribute does not exist %s.%s" % (cls.__name__, key))
                continue
            if isinstance(getattr(cls, key), AbstractEnum) and not isinstance(value, AbstractEnum):
                raise SongDataError("inconsistent AbstractEnum value for %s.%s : got %s" % (cls_fqdn, key, value))
            setattr(cls, key, value)

    def clear(self):
        # type: () -> None
        Logger.log_info("Clearing song data of %s" % InterfaceState)
        self._set_data(str(InterfaceState), {})
