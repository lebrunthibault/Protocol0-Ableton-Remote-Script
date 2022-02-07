import collections
from itertools import chain

from typing import Optional, List

import Live
from protocol0.domain.lom.Listenable import Listenable
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.BeatChangedEvent import BeatChangedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SongScenesManager(Listenable):
    def __init__(self):
        # type: () -> None
        super(SongScenesManager, self).__init__()
        self.scenes_listener.subject = SongFacade.live_song()
        DomainEventBus.subscribe(BeatChangedEvent, self._beat_changed_listener)
        self._live_scene_id_to_scene = collections.OrderedDict()

    def get_scene(self, live_scene):
        # type: (Live.Scene.Scene) -> Scene
        return self._live_scene_id_to_scene[live_scene._live_ptr]

    def get_optional_scene(self, scene):
        # type: (Live.Scene.Scene) -> Optional[Scene]
        try:
            return self.get_scene(scene)
        except KeyError:
            return None

    def add_scene(self, scene):
        # type: (Scene) -> None
        self._live_scene_id_to_scene[scene.live_id] = scene

    @property
    def scenes(self):
        # type: () -> List[Scene]
        return self._live_scene_id_to_scene.values()

    @p0_subject_slot("scenes")
    def scenes_listener(self):
        # type: () -> None
        self._generate_scenes()
        for scene in SongFacade.scenes():
            Scheduler.defer(scene.refresh_appearance)
        Logger.log_info("mapped scenes")

    def _beat_changed_listener(self, _):
        # type: (BeatChangedEvent) -> None
        if SongFacade.playing_scene() and SongFacade.playing_scene().has_playing_clips:
            SongFacade.playing_scene().on_beat_changed()

    def _generate_scenes(self):
        # type: () -> None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        for track in collections.OrderedDict.fromkeys(chain(SongFacade.simple_tracks(), SongFacade.abstract_tracks())):
            track.on_scenes_change()

        live_scenes = SongFacade.live_song().scenes
        has_added_scene = 0 < len(SongFacade.scenes()) < len(live_scenes)

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        if has_added_scene and SongFacade.selected_scene().length and SongFacade.is_playing():
            Scheduler.defer(SongFacade.selected_scene().fire)

    def _clean_deleted_scenes(self):
        # type: () -> None
        existing_scene_ids = [scene._live_ptr for scene in SongFacade.live_song().scenes]
        deleted_ids = []

        for scene_id, scene in self._live_scene_id_to_scene.items():
            if scene_id not in existing_scene_ids:
                scene.disconnect()

        for scene_id in deleted_ids:
            del self._live_scene_id_to_scene[scene_id]

    def generate_scene(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        scene = self.get_optional_scene(live_scene)
        if scene is None:
            scene = Scene(live_scene, index=index)
        else:
            scene.index = index

        self.add_scene(scene)

    def _sort_scenes(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for scene in SongFacade.live_song().scenes:
            sorted_dict[scene._live_ptr] = self.get_scene(scene)
        self._live_scene_id_to_scene = sorted_dict

    def delete_empty_scenes(self):
        # type: () -> Sequence
        empty_scenes = []
        seq = Sequence()
        for scene in reversed(SongFacade.scenes()):
            if scene.length == 0:
                empty_scenes.append(scene)
            else:
                break

        seq.add([scene.delete for scene in empty_scenes])
        return seq.done()

    def scroll_scenes(self, go_next):
        # type: (bool) -> None
        scroll_values(SongFacade.scenes(), SongFacade.selected_scene(), go_next, rotate=False).select()
