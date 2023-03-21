import re

from typing import List, Iterator, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.group_track.ext_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.special.ResamplingTrack import ResamplingTrack
from protocol0.domain.shared.utils.timing import debounce
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SceneClipSlot(object):
    def __init__(self, track, clip_slot):
        # type: (SimpleTrack, ClipSlot) -> None
        self.track = track
        self.clip_slot = clip_slot
        self.is_main_clip = not isinstance(track, SimpleAudioExtTrack)

    def __repr__(self):
        # type: () -> str
        return "SceneClips(%s, %s)" % (self.track, self.clip)

    @property
    def clip(self):
        # type: () -> Optional[Clip]
        if self.clip_slot.has_clip and not isinstance(self.track, ResamplingTrack):
            return self.clip_slot.clip
        else:
            return None


class SceneClips(Observable):
    def __init__(self, index):
        # type: (int) -> None
        super(SceneClips, self).__init__()
        self.index = index
        self._clip_slot_tracks = []  # type: List[SceneClipSlot]

        self.build()

    def __repr__(self):
        # type: () -> str
        return "SceneClips(%s)" % self.index

    def __iter__(self):
        # type: () -> Iterator[Clip]
        return iter(
            scene_cs.clip
            for scene_cs in self._clip_slot_tracks
            if scene_cs.clip is not None and scene_cs.is_main_clip
        )

    @property
    def all(self):
        # type: () -> List[Clip]
        return [scene_cs.clip for scene_cs in self._clip_slot_tracks if scene_cs.clip is not None]

    @property
    def tracks(self):
        # type: () -> List[SimpleTrack]
        return [scene_clip.track for scene_clip in self._clip_slot_tracks]

    @debounce(duration=50)
    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ClipSlot) or isinstance(observable, Clip):
            self.build()
            self.notify_observers()

    def build(self):
        # type: () -> None
        self._clip_slot_tracks = []

        for track in Song.simple_tracks():
            clip_slot = track.clip_slots[self.index]
            clip_slot.register_observer(self)
            self._clip_slot_tracks.append(SceneClipSlot(track, clip_slot))

        for clip in self:
            clip.register_observer(self)

    def on_added_scene(self):
        # type: () -> None
        """Renames clips when doing consolidate time to new scene"""
        if any(clip for clip in self.all if self._clip_has_default_recording_name(clip)):
            for clip in self.all:
                if self._clip_has_default_recording_name(clip):
                    clip.appearance.color = ClipColorEnum.AUDIO_UN_QUANTIZED.value
                clip.clip_name.update("")

    def _clip_has_default_recording_name(self, clip):
        # type: (Clip) -> bool
        return bool(re.match(".*\\[\\d{4}-\\d{2}-\\d{2} \\d+]$", clip.name))
