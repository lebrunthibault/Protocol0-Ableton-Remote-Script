import re
import time

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.string import title
from protocol0.domain.shared.utils.utils import get_length_legend
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class SceneName(SlotManager):
    def __init__(self, scene, scene_length, scene_playing_state):
        # type: (Live.Scene.Scene, SceneLength, ScenePlayingState) -> None
        super(SceneName, self).__init__()
        self._scene = scene
        self._scene_length = scene_length
        self._scene_playing_state = scene_playing_state
        self._name_listener.subject = scene
        self._last_updated_at = time.time()
        self._cached_name = self._scene.name  # type: str

    def __repr__(self):
        # type: () -> str
        return "name of %s" % self._scene

    def set_name(self, name):
        # type: (str) -> None
        self._scene.name = title(name)
        self._cached_name = self._scene.name

    @subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        if time.time() >= self._last_updated_at + 0.1:
            Scheduler.defer(self.update)

    def _get_base_name(self):
        # type: () -> str
        if not self._scene:
            raise Protocol0Error("invalid scene object")

        # remove the looping marker
        scene_name = re.sub("^\\*+", "", str(self._scene.name))

        # catches base name with or without bar length legend
        forbidden_first_character = "(?!([\\d|-]+))"
        match = re.match("^(?P<base_name>%s[^()]*)" % forbidden_first_character, scene_name)
        base_name = match.group("base_name").strip() if match else ""

        return base_name

    def update(self, base_name=None, bar_position=None):
        # type: (str, Optional[int]) -> None
        """throttling to avoid multiple calls due to name listener"""
        try:
            base_name = base_name if base_name else self._get_base_name()
        except Protocol0Error as e:
            Logger.warning(str(e))
            self.disconnect()
            return

        if (
            not float(self._scene_length.length).is_integer()
            or self._scene_length.length == Config.CLIP_MAX_LENGTH
        ):
            length_legend = ""  # we are recording
        else:
            length_legend = get_length_legend(
                self._scene_length.length,
                Song.signature_numerator(),
            )

        if self._scene_playing_state.is_playing:
            length_legend = "%s|%s" % (self._scene_playing_state.current_bar + 1, length_legend)
        elif bar_position is not None:
            length_legend = "%s|%s" % (bar_position + 1, length_legend)

        if base_name:
            scene_name = "%s (%s)" % (base_name, length_legend)
        else:
            scene_name = "%s" % length_legend

        if Song.looping_scene() and Song.looping_scene()._scene == self._scene:
            scene_name = "*%s" % scene_name

        self.set_name(scene_name)
        self._last_updated_at = time.time()
