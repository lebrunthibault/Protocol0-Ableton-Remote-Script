from typing import cast

from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.ValueToggler import ValueToggler
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class LoopingSceneToggler(ValueToggler):
    def __init__(self):
        # type: () -> None
        super(LoopingSceneToggler, self).__init__()
        DomainEventBus.subscribe(PlayingSceneChangedEvent, self._on_playing_scene_changed_event)

    def _on_playing_scene_changed_event(self, _):
        # type: (PlayingSceneChangedEvent) -> None
        if self.value and self.value != Song.playing_scene():
            self.reset()

    def _get_value(self):
        # type: () -> Scene
        if Song.is_playing():
            return cast(Scene, Song.playing_scene())
        else:
            return Song.selected_scene()

    def _value_set(self, scene):
        # type: (Scene) -> None
        scene.scene_name.update()

    def _value_unset(self, scene):
        # type: (Scene) -> None
        scene.scene_name.update()
