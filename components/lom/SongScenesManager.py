import collections
from itertools import chain

from typing import Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.Scene import Scene
from protocol0.utils.decorators import p0_subject_slot


class SongScenesManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongScenesManager, self).__init__(*a, **k)
        self.scenes_listener.subject = self.song._song

    @p0_subject_slot("scenes")
    def scenes_listener(self):
        # type: () -> None
        self.parent.sceneBeatScheduler.clear()

        self._generate_scenes()
        self.parent.defer(lambda: [scene.refresh_appearance() for scene in self.song.scenes])
        self.parent.log_info("mapped scenes")

    @p0_subject_slot("tracks")
    def _generate_scenes(self):
        # type: () -> None
        for track in chain(self.song.all_simple_tracks, self.song.abstract_tracks):
            track.on_scenes_change()

        self.song.live_clip_slot_to_clip_slot = {
            clip_slot._clip_slot: clip_slot for track in self.song.simple_tracks for clip_slot in track.clip_slots
        }

        live_scenes = self.song._song.scenes
        has_added_scene = len(self.song.scenes) and len(live_scenes) > len(self.song.scenes)

        # disconnect removed scenes
        for scene in self.song.scenes:
            if scene._scene not in live_scenes:
                scene.disconnect()
            # when moving scenes around
            elif list(live_scenes).index(scene._scene) != scene.index:
                scene.disconnect()
                self.song.scenes.remove(scene)

        # create a dict access from live scenes
        scene_mapping = collections.OrderedDict()
        for scene in self.song.scenes:
            scene_mapping[scene._scene] = scene

        new_scenes = []

        # get the right scene or instantiate new scenes
        for live_scene in live_scenes:
            if live_scene in scene_mapping:
                scene = scene_mapping[live_scene]
            else:
                scene = Scene(live_scene)
            scene.link_clip_slots_and_clips()

            new_scenes.append(scene)

        self.song.scenes[:] = new_scenes

        if has_added_scene and self.song.selected_scene and self.song.selected_scene.length and self.song.is_playing:
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.song.selected_scene.fire)
