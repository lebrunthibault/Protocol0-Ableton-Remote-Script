import Live
from typing import List

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SceneName import SceneName
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.AudioBusTrack import AudioBusTrack
from a_protocol_0.utils.decorators import p0_subject_slot


class Scene(AbstractObject):
    def __init__(self, scene, index, *a, **k):
        # type: (Live.Scene.Scene, int) -> None
        super(Scene, self).__init__(*a, **k)
        self.index = index
        self._scene = scene
        self.scene_name = SceneName(self)
        self._is_triggered_listener.subject = self._scene
        self.clip_slots = [
            self.song.clip_slots_by_live_live_clip_slot[clip_slot] for clip_slot in self._scene.clip_slots
        ]  # type: List[ClipSlot]

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        """
        implements a next scene follow action
        when the scene is triggered (e.g. clicked or fired via script) the scheduler is cleared
        when the scene starts playing we schedule firing the next scene after this one ended
        NB : self.is_triggered == False can mean 3 things :
        - the scene is playing (usual case): the we schedule the next one
        - the song is stopped : we check this
        - another scene is launched : that's why we stop the scheduler when is_triggered is True
        """
        if self.is_triggered:
            self.parent.sceneBeatScheduler.clear()
        # doing this when scene starts playing
        elif not self.looping:
            self._schedule_next_scene_launch()

    def _schedule_next_scene_launch(self):
        if self.index == len(self.song.scenes) - 1:
            return
        next_scene = self.song.scenes[self.index + 1]
        self.parent.sceneBeatScheduler.wait_beats(self.length - self.playing_position, next_scene.fire)

    def select(self):
        self.song.selected_scene = self

    def fire(self):
        if self._scene:
            self._scene.fire()

    def play_stop(self):
        self.fire()

    def toggle_solo(self):
        """ for a scene solo means looped """
        if not self.looping:  # solo activation
            previous_looping_scene = self.song.looping_scene
            self.song.looping_scene = self
            self.fire()
            if previous_looping_scene:
                previous_looping_scene.scene_name.update()
            self.parent.sceneBeatScheduler.clear()  # clearing scene scheduling
        else:  # solo inactivation
            self.song.looping_scene = None
            self._schedule_next_scene_launch()  # restore previous behavior of follow action
        self.scene_name.update()

    @property
    def color(self):
        # type: () -> int
        return self._scene.color

    @color.setter
    def color(self, color):
        self._scene.color = color

    @property
    def is_triggered(self):
        # type: () -> int
        return self._scene.is_triggered

    @property
    def name(self):
        # type: () -> int
        return self._scene.name

    @name.setter
    def name(self, name):
        if self._scene and name:
            self._scene.name = str(name).strip()

    @property
    def length(self):
        # type: () -> int
        return self.longest_clip.length if self.longest_clip else 0

    @property
    def bar_length(self):
        # type: () -> int
        return self.length / self.song.signature_denominator

    @property
    def playing_position(self):
        # type: () -> int
        return self.longest_clip.playing_position if self.longest_clip else 0

    @property
    def looping(self):
        # type: () -> bool
        return self == self.song.looping_scene

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip
            for clip_slot in self.clip_slots
            if clip_slot.has_clip and not isinstance(clip_slot.track, AudioBusTrack)
        ]

    @property
    def longest_clip(self):
        # type: () -> Clip
        return None if not len(self.clips) else max(self.clips, key=lambda c: c.length)
