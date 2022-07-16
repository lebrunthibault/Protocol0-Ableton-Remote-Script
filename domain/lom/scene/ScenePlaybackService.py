import collections
from functools import partial

from _Framework.SubjectSlot import SlotManager
from typing import Optional, Dict

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ScenePlaybackService(SlotManager):
    _DEBUG = False

    def __init__(self, playback_component):
        # type: (PlaybackComponent) -> None
        super(ScenePlaybackService, self).__init__()
        self._playback_component = playback_component

        self._live_scene_id_to_scene = collections.OrderedDict()  # type: Dict[int, Scene]

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)
        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        if SongFacade.playing_scene():
            SongFacade.playing_scene().scene_name.update()

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        if (
            SongFacade.playing_scene()
            and SongFacade.playing_scene().playing_state.has_playing_clips
        ):
            SongFacade.playing_scene().on_last_beat()

    def _on_scene_position_scrolled_event(self, _):
        # type: (ScenePositionScrolledEvent) -> None
        scene = SongFacade.selected_scene()
        Scene.LAST_MANUALLY_STARTED_SCENE = scene
        scene.scene_name.update(bar_position=scene.position_scroller.current_value)

    def fire_selected_scene(self):
        # type: () -> Optional[Sequence]
        self._playback_component.stop_all_clips(quantized=False)
        self._playback_component.stop_playing()
        SongFacade.selected_scene().fire()
        return None

    def fire_scene_to_position(self, scene, bar_length=None):
        # type: (Scene, Optional[int]) -> None
        bar_length = self._get_position_bar_length(scene, bar_length)
        Scene.LAST_MANUALLY_STARTED_SCENE = scene
        self._playback_component.stop_playing()

        if self._DEBUG:
            Logger.info("Firing %s to bar_length %s" % (scene, bar_length))

        if bar_length != 0:
            # removing click when changing position
            # (created by playing shortly the scene beginning)
            SongFacade.master_track().mute_for(50)

        Scheduler.wait(2, partial(scene.fire_to_position, bar_length))

    def fire_previous_scene_to_last_bar(self):
        # type: () -> None
        previous_scene = SongFacade.selected_scene().previous_scene
        if previous_scene == SongFacade.selected_scene():
            self.fire_selected_scene()
            return None

        self.fire_scene_to_position(previous_scene, previous_scene.bar_length - 1)

    def _get_position_bar_length(self, scene, bar_length):
        # type: (Scene, Optional[int]) -> int
        # as we use single digits
        if bar_length == 8:
            return scene.bar_length - 1
        if bar_length is None:
            return scene.position_scroller.current_value

        return bar_length
