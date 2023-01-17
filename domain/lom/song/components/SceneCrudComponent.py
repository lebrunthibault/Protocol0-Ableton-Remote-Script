from functools import partial

from typing import Optional, Callable

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneWindow import SceneWindow
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SceneCrudComponent(object):
    def __init__(self, create_scene, duplicate_scene, delete_scene):
        # type: (Callable, Callable, Callable) -> None
        self._create_scene = create_scene
        self._duplicate_scene = duplicate_scene
        self._delete_scene = delete_scene

    def create_scene(self, scene_index=None):
        # type: (Optional[int]) -> Sequence
        seq = Sequence()
        scenes_count = len(Song.scenes())
        seq.add(partial(self._create_scene, scene_index or scenes_count))
        seq.wait_for_event(ScenesMappedEvent)
        seq.defer()
        return seq.done()

    def duplicate_scene(self, scene):
        # type: (Scene) -> Sequence
        seq = Sequence()
        seq.add(partial(self._duplicate_scene, scene.index))
        seq.wait_for_event(ScenesMappedEvent)
        return seq.done()

    def split_scene(self, scene):
        # type: (Scene) -> Sequence
        start_window, end_window = SceneWindow.create_from_split(
            scene.length, scene.crop_scroller.current_value
        )
        seq = Sequence()
        seq.add(partial(self.duplicate_scene, scene))
        seq.add(partial(start_window.apply_to_scene, scene.clips))
        seq.defer()
        seq.add(lambda: end_window.apply_to_scene(Song.selected_scene().clips))

        return seq.done()

    def crop_scene(self, scene):
        # type: (Scene) -> Sequence
        window = SceneWindow.create_from_crop(scene.length, scene.crop_scroller.current_value)
        seq = Sequence()
        seq.add(partial(self.duplicate_scene, scene))
        seq.defer()
        seq.add(lambda: window.apply_to_scene(Song.selected_scene().clips))

        return seq.done()

    def delete_scene(self, scene):
        # type: (Scene) -> Optional[Sequence]
        if len(Song.scenes()) == 1:
            Logger.warning("Cannot delete last scene")
            return None

        seq = Sequence()
        seq.add(partial(self._delete_scene, scene.index))
        seq.wait_for_event(ScenesMappedEvent)
        seq.defer()
        return seq.done()
