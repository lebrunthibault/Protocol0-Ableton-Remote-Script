from typing import Optional, List, TYPE_CHECKING

from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
    from protocol0.domain.lom.scene.Scene import Scene


class PlayingSceneFacade(object):
    _INSTANCE = None  # type: Optional[PlayingSceneFacade]

    def __init__(self, scene_component):
        # type: (SceneComponent) -> None
        PlayingSceneFacade._INSTANCE = self

        self._scene_component = scene_component
        self._last_playing_scenes = [None] * 5  # type: List[Optional[Scene]]

    @classmethod
    def get(cls):
        # type: () -> Optional[Scene]
        return cls._INSTANCE._last_playing_scenes[-1]

    @classmethod
    def get_previous(cls):
        # type: () -> Optional[Scene]
        return cls._INSTANCE._last_playing_scenes[-2]

    @classmethod
    def set(cls, scene):
        # type: (Optional[Scene]) -> None
        if scene == cls.get():
            return None

        scenes = cls._INSTANCE._last_playing_scenes
        cls._INSTANCE._last_playing_scenes = scenes[1:] + [scene]

        # and select it
        if scene is not None:
            cls._INSTANCE._scene_component.select_scene(scene)

        DomainEventBus.emit(PlayingSceneChangedEvent())

        # deferring this until the previous playing scene has stopped
        # Scheduler.wait_ms(500, cls._check_for_unknown_playing_scenes)

    @classmethod
    def history(cls):
        # type: () -> List[Optional[Scene]]
        return cls._INSTANCE._last_playing_scenes

    @classmethod
    def _check_for_unknown_playing_scenes(cls):
        # type: () -> None
        """
            Monitoring method to find out
            why some scenes are left out of the playing scene pattern
        """
        unknown_playing_scenes = []
        for scene in Song.scenes():
            if scene.playing_state.is_playing and scene != cls.get():
                unknown_playing_scenes.append(scene)

        history = list(reversed(cls.history()))
        for scene in unknown_playing_scenes:
            Logger.warning("Unknown playing scene %s" % scene)
            if scene in history:
                Logger.warning("In history at index : -%s" % (history.index(scene) + 1))

        if len(unknown_playing_scenes) > 0:
            Logger.info("PlayingScene history: %s" % cls.history())
            Backend.client().show_warning("unknown playing scene found")
            for scene in unknown_playing_scenes:
                scene.stop(immediate=True)
