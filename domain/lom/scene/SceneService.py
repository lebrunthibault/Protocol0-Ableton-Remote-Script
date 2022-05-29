import collections
from functools import partial
from itertools import chain

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional, List, Iterator, Dict

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import volume_to_db
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SceneService(SlotManager):
    _DEBUG = True

    def __init__(self, live_song, playback_component, scene_crud_component):
        # type: (Live.Song.Song, PlaybackComponent, SceneCrudComponent) -> None
        super(SceneService, self).__init__()
        self._live_song = live_song
        self._playback_component = playback_component
        self._scene_crud_component = scene_crud_component

        self.scenes_listener.subject = live_song
        self._selected_scene_listener.subject = live_song.view
        self._live_scene_id_to_scene = collections.OrderedDict()  # type: Dict[int, Scene]

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)
        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)
        DomainEventBus.subscribe(TrackAddedEvent, self._on_track_added_event)
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)

    def get_scene(self, live_scene):
        # type: (Live.Scene.Scene) -> Scene
        return self._live_scene_id_to_scene[live_scene._live_ptr]

    def add_scene(self, scene):
        # type: (Scene) -> None
        self._live_scene_id_to_scene[scene.live_id] = scene

    @property
    def scenes(self):
        # type: () -> List[Scene]
        return self._live_scene_id_to_scene.values()

    @property
    def last_scene(self):
        # type: () -> Scene
        current_scene = self.scenes[0]
        while current_scene.next_scene and current_scene.next_scene != current_scene:
            current_scene = current_scene.next_scene

        return current_scene

    @subject_slot("scenes")
    @handle_error
    def scenes_listener(self):
        # type: () -> None
        previous_live_scenes_ids = self._live_scene_id_to_scene.keys()

        self._generate_scenes()
        for scene in SongFacade.scenes():
            if len(previous_live_scenes_ids) and scene.live_id not in previous_live_scenes_ids:
                Scheduler.defer(scene.on_added)

        DomainEventBus.defer_emit(ScenesMappedEvent())
        Logger.info("mapped scenes")

    @subject_slot("selected_scene")
    @handle_error
    def _selected_scene_listener(self):
        # type: () -> None
        DomainEventBus.emit(SessionUpdatedEvent())

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        if SongFacade.playing_scene():
            SongFacade.playing_scene().scene_name.update()

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        if SongFacade.playing_scene() and SongFacade.playing_scene().playing_state.has_playing_clips:
            SongFacade.playing_scene().on_last_beat()

    def _generate_scenes(self):
        # type: () -> None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        tracks = chain(SongFacade.simple_tracks(), SongFacade.abstract_tracks())  # type: Iterator[AbstractTrack]
        for track in collections.OrderedDict.fromkeys(tracks):
            track.on_scenes_change()

        live_scenes = self._live_song.scenes
        has_added_scene = 0 < len(SongFacade.scenes()) < len(live_scenes)

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        if has_added_scene and SongFacade.selected_scene().length and SongFacade.is_playing():
            Scheduler.defer(SongFacade.selected_scene().fire)

    def _clean_deleted_scenes(self):
        # type: () -> None
        existing_scene_ids = [scene._live_ptr for scene in self._live_song.scenes]

        for scene_id, scene in self._live_scene_id_to_scene.items():
            # cleaning all scenes always
            scene.disconnect()
            if scene == Scene.PLAYING_SCENE:
                Scene.PLAYING_SCENE = None

            # refresh the mapping
            if scene_id not in existing_scene_ids:
                del self._live_scene_id_to_scene[scene_id]

    def generate_scene(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        # switching to full remap because of persisting mapping problems when moving scenes
        scene = Scene(live_scene, index)
        self.add_scene(scene)

    def _sort_scenes(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for scene in self._live_song.scenes:
            sorted_dict[scene._live_ptr] = self.get_scene(scene)
        self._live_scene_id_to_scene = sorted_dict

    def _on_track_added_event(self, _):
        # type: (TrackAddedEvent) -> Sequence
        empty_scenes = []
        seq = Sequence()
        for scene in list(reversed(SongFacade.scenes()))[1:]:
            if scene.length == 0:
                empty_scenes.append(scene)
            else:
                break

        seq.add([partial(self._scene_crud_component.delete_scene, scene) for scene in empty_scenes])
        return seq.done()

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

        master_volume = SongFacade.master_track().volume
        if bar_length != 0:
            SongFacade.master_track().volume = volume_to_db(0)

        # removing click when changing position
        # (created by playing shortly the scene beginning)
        Scheduler.wait(2, partial(scene.fire_to_position, bar_length))
        # duplicate the volume set because sometimes it is skipped
        Scheduler.wait(3, (partial(setattr, SongFacade.master_track(), "volume", master_volume)))
        Scheduler.wait(10, (partial(setattr, SongFacade.master_track(), "volume", master_volume)))

    def _get_position_bar_length(self, scene, bar_length):
        # type: (Scene, Optional[int]) -> int
        # as we use single digits
        if bar_length == 8:
            return scene.bar_length - 1
        if bar_length is None:
            return scene.position_scroller.current_value

        return bar_length
