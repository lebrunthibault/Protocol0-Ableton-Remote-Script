import collections
from itertools import chain

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import List, Iterator, Dict

from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.error_handler import handle_error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import debounce
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SceneService(SlotManager):
    # noinspection PyInitNewSignature
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
        return list(self._live_scene_id_to_scene.values())

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
        for scene in Song.scenes():
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
        # save playing scene
        playing_live_scene = Song.playing_scene()._scene if Song.playing_scene() else None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        tracks = chain(
            Song.simple_tracks(), Song.abstract_tracks()
        )  # type: Iterator[AbstractTrack]
        for track in collections.OrderedDict.fromkeys(tracks):
            track.on_scenes_change()

        live_scenes = self._live_song.scenes

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        # restore playing scene
        if playing_live_scene is not None:
            playing_scene = find_if(lambda s: s._scene == playing_live_scene, Song.scenes())
            PlayingSceneFacade.set(playing_scene)

    def _clean_deleted_scenes(self):
        # type: () -> None
        """cleaning all scenes always"""
        existing_scene_ids = [scene._live_ptr for scene in self._live_song.scenes]

        for scene_id, scene in self._live_scene_id_to_scene.copy().items():
            # refresh the mapping
            if scene_id not in existing_scene_ids:
                # checking on name and not bar_length
                if len(Song.scenes()) > 5 and scene.name != "0":
                    Backend.client().show_warning("You just deleted %s" % scene)

                del self._live_scene_id_to_scene[scene_id]

            scene.disconnect()
            if scene == Song.playing_scene():
                PlayingSceneFacade.set(None)


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
        seq = Sequence()

        def delete_empty_scenes():
            # type: () -> None
            for scene in list(reversed(Song.scenes()))[1:]:
                if len(scene.clips.all) == 0:
                    self._scene_crud_component.delete_scene(scene)
                else:
                    return

        seq.wait_ms(1000)  # wait for the track clips to be populated
        seq.add(delete_empty_scenes)
        return seq.done()
