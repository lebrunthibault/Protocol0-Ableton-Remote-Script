import collections
from itertools import chain

from typing import Any, Optional, List

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.Scene import Scene
from protocol0.utils.decorators import p0_subject_slot


class SongScenesManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongScenesManager, self).__init__(*a, **k)
        self.scenes_listener.subject = self.song._song
        self._live_scene_id_to_scene = collections.OrderedDict()

    def get_scene(self, live_scene):
        # type: (Live.Scene.Scene) -> Scene
        return self._live_scene_id_to_scene[live_scene._live_ptr]

    def _get_optional_scene(self, scene):
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
        self.parent.sceneBeatScheduler.clear()

        self._generate_scenes()
        self.parent.defer(lambda: [scene.refresh_appearance() for scene in self.song.scenes])
        self.parent.log_info("mapped scenes")

    def _generate_scenes(self):
        # type: () -> None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        for track in collections.OrderedDict.fromkeys(chain(self.song.simple_tracks, self.song.abstract_tracks)):
            track.on_scenes_change()

        live_scenes = self.song._song.scenes
        has_added_scene = 0 < len(self.song.scenes) < len(live_scenes)

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        if has_added_scene and self.song.selected_scene.length and self.song.is_playing:
            self.parent.defer(self.song.selected_scene.fire)

    def _clean_deleted_scenes(self):
        # type: () -> None
        existing_scene_ids = [scene._live_ptr for scene in self.song._song.scenes]
        deleted_ids = []

        for scene_id, scene in self._live_scene_id_to_scene.items():
            if scene_id not in existing_scene_ids:
                scene.disconnect()

        for scene_id in deleted_ids:
            del self._live_scene_id_to_scene[scene_id]

    def generate_scene(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        scene = self._get_optional_scene(live_scene)
        if scene is None:
            scene = Scene(live_scene, index=index)
        else:
            scene.index = index

        self.add_scene(scene)

    def _sort_scenes(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for scene in self.song._song.scenes:
            sorted_dict[scene._live_ptr] = self.get_scene(scene)
        self._live_scene_id_to_scene = sorted_dict
