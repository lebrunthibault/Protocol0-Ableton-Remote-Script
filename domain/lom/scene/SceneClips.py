import re

from typing import List, cast, Iterator

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.simple_track.InstrumentBusTrack import InstrumentBusTrack
from protocol0.domain.lom.track.simple_track.ResamplingTrack import ResamplingTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.timing import debounce
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SceneClip(object):
    def __init__(self, track, clip):
        # type: (SimpleTrack, Clip) -> None
        self.track = track
        self.clip = clip
        self.is_main_clip = not isinstance(
            track, (SimpleAudioExtTrack, SimpleAudioTailTrack, SimpleDummyTrack)
        )

    def __repr__(self):
        # type: () -> str
        return "SceneClips(%s, %s)" % (self.track, self.clip)


class SceneClips(Observable):
    def __init__(self, index):
        # type: (int) -> None
        super(SceneClips, self).__init__()
        self.index = index
        self._clip_tracks = []  # type: List[SceneClip]
        self._clips = []  # type: List[Clip]

        self.build()

    def __repr__(self):
        # type: () -> str
        return "SceneClips(%s)" % self.index

    def __iter__(self):
        # type: () -> Iterator[Clip]
        return iter(self._clips)

    @property
    def all(self):
        # type: () -> List[Clip]
        return [scene_clip.clip for scene_clip in self._clip_tracks]

    @property
    def audio_tail_clips(self):
        # type: () -> List[AudioTailClip]
        return cast(List[AudioTailClip], [c for c in self.all if isinstance(c, AudioTailClip)])

    @property
    def tracks(self):
        # type: () -> List[SimpleTrack]
        return [scene_clip.track for scene_clip in self._clip_tracks]

    @debounce(duration=50)
    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ClipSlot) or isinstance(observable, Clip):
            self.build()
            self.notify_observers()

    def build(self):
        # type: () -> None
        self._clip_tracks = []

        for track in Song.simple_tracks():
            clip_slot = track.clip_slots[self.index]
            clip_slot.register_observer(self)
            clip = clip_slot.clip
            if (
                clip is not None
                and clip_slot.has_clip
                and type(track) not in (InstrumentBusTrack, ResamplingTrack)
            ):
                self._clip_tracks.append(SceneClip(track, clip))

        self._clips = [
            scene_clip.clip for scene_clip in self._clip_tracks if scene_clip.is_main_clip
        ]

        for clip in self:
            clip.register_observer(self)

    def on_added_scene(self):
        # type: () -> None
        """Renames clips when doing consolidate time to new scene"""
        if any(clip for clip in self.all if self._clip_has_default_recording_name(clip)):
            for clip in self.all:
                if self._clip_has_default_recording_name(clip):
                    clip.appearance.color = ClipColorEnum.AUDIO_UN_QUANTIZED.int_value
                clip.clip_name.update("")

    def _clip_has_default_recording_name(self, clip):
        # type: (Clip) -> bool
        return bool(re.match(".*\\[\\d{4}-\\d{2}-\\d{2} \\d+]$", clip.name))
