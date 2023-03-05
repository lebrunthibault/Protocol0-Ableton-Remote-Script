import Live

from protocol0.domain.lom.scene.LoopingSceneToggler import LoopingSceneToggler
from protocol0.domain.lom.scene.NextSceneStartedEvent import NextSceneStartedEvent
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.event.RecordStartedEvent import RecordStartedEvent
from protocol0.shared.Song import Song


class SceneComponent(object):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        self._song_view = song_view
        self.looping_scene_toggler = LoopingSceneToggler()  # type: LoopingSceneToggler

        DomainEventBus.subscribe(RecordStartedEvent, self._on_record_started_event)
        DomainEventBus.subscribe(NextSceneStartedEvent, self._on_next_scene_started_event)

    def _on_record_started_event(self, event):
        # type: (RecordStartedEvent) -> None
        self.looping_scene_toggler.reset()
        if event.scene_index != Song.selected_scene().index:
            self.select_scene(Song.scenes()[event.scene_index])

    def select_scene(self, scene):
        # type: (Scene) -> None
        self._song_view.selected_scene = scene._scene

    def scroll_scenes(self, go_next):
        # type: (bool) -> None
        # have the scroller work the other way around
        go_next = not go_next
        next_scene = ValueScroller.scroll_values(
            Song.scenes(), Song.selected_scene(), go_next, rotate=False
        )
        self.select_scene(next_scene)

    def _on_next_scene_started_event(self, event):
        # type: (NextSceneStartedEvent) -> None
        """Event is fired *before* the scene starts playing"""
        # Stop the previous scene : quantized or immediate
        try:
            previous_selected_scene = Song.scenes()[event.selected_scene_index]
        except IndexError:
            return

        if (
            previous_selected_scene != Song.selected_scene()
            and ApplicationView.is_clip_view_visible()
        ):
            self.select_scene(previous_selected_scene)
