import collections
from functools import partial
from itertools import chain

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import List, Iterator, Dict

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.decorators import handle_error, debounce
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SceneService(SlotManager):
    def __init__(self, live_song, scene_crud_component):
        # type: (Live.Song.Song, SceneCrudComponent) -> None
        super(SceneService, self).__init__()
        self._live_song = live_song
        self._scene_crud_component = scene_crud_component

        self.scenes_listener.subject = live_song
        self._selected_scene_listener.subject = live_song.view
        self._live_scene_id_to_scene = collections.OrderedDict()  # type: Dict[int, Scene]

        DomainEventBus.subscribe(TrackAddedEvent, self._on_track_added_event)

    def get_scene(self, live_scene):
        # type: (Live.Scene.Scene) -> Scene
        return self._live_scene_id_to_scene[live_scene._live_ptr]

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
    @debounce(duration=50)
    def _selected_scene_listener(self):
        # type: () -> None
        """
        debounce necessary when multiple scenes are added at the same time
        (e.g. when importing a track)
        """
        DomainEventBus.emit(SessionUpdatedEvent())

    def _generate_scenes(self):
        # type: () -> None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        tracks = chain(
            SongFacade.simple_tracks(), SongFacade.abstract_tracks()
        )  # type: Iterator[AbstractTrack]
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
        self._live_scene_id_to_scene[scene.live_id] = scene

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
            # nb : scene.length == 0 would suppress the template dummy clip
            if len(scene.clips.all) == 0:
                empty_scenes.append(scene)
            else:
                break

        seq.add([partial(self._scene_crud_component.delete_scene, scene) for scene in empty_scenes])
        return seq.done()
