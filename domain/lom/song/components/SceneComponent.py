import Live

from protocol0.domain.lom.scene.LoopingSceneToggler import LoopingSceneToggler
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.TrackRecordingStartedEvent import TrackRecordingStartedEvent
from protocol0.shared.SongFacade import SongFacade


class SceneComponent(object):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        self._song_view = song_view
        self.looping_scene_toggler = LoopingSceneToggler()  # type: LoopingSceneToggler

        DomainEventBus.subscribe(TrackRecordingStartedEvent, self._on_track_recording_started_event)

    def _on_track_recording_started_event(self, event):
        # type: (TrackRecordingStartedEvent) -> None
        self.looping_scene_toggler.reset()
        if event.recording_scene_index != SongFacade.selected_scene().index:
            self.select_scene(SongFacade.scenes()[event.recording_scene_index])

    def select_scene(self, scene):
        # type: (Scene) -> None
        self._song_view.selected_scene = scene._scene

    def scroll_scenes(self, go_next):
        # type: (bool) -> None
        # have the scroller work the other way around
        go_next = not go_next
        next_scene = ValueScroller.scroll_values(
            SongFacade.scenes(), SongFacade.selected_scene(), go_next, rotate=False
        )
        self.select_scene(next_scene)
