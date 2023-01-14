from functools import partial

from typing import List, cast, Optional, Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioMatchingTrack import (
    SimpleAudioMatchingTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self.matching_track = SimpleAudioMatchingTrack(self)

    @property
    def clip_slots(self):
        # type: () -> List[AudioClipSlot]
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return cast(List[AudioClip], super(SimpleAudioTrack, self).clips)

    @property
    def playing_clip(self):
        # type: () -> Optional[AudioClip]
        return super(SimpleAudioTrack, self).playing_clip

    def has_same_clips(self, track):
        # type: (AbstractTrack) -> bool
        if not isinstance(track, SimpleAudioTrack):
            return False

        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def post_flatten(self):
        # type: () -> None
        for clip in self.clips:
            clip.looping = True

    def load_matching_track(self):
        # type: () -> Sequence
        assert isinstance(SongFacade.current_track(), SimpleAudioTrack), "Track already loaded"
        matching_track = find_if(
            lambda t: t != self and t.name == self.name and not t.is_foldable,
            SongFacade.simple_tracks(),
        )
        if matching_track is not None:
            matching_track.select()
            raise Protocol0Warning("Track already loaded")

        track_color = self.color
        seq = Sequence()
        seq.add(self.focus)
        seq.add(Backend.client().drag_matching_track)
        seq.wait_for_backend_event("track_focused")
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("matching_track_loaded")
        return seq.done()

    def restore_clip_color(self):
        # type: () -> None
        for clip in self.clips:
            if clip.color == ClipColorEnum.HAS_AUTOMATION.value:
                clip.color = self.color

    def disconnect(self):
        # type: () -> None
        super(SimpleAudioTrack, self).disconnect()
        matching_track = AbstractMatchingTrack.get_matching_track(self)
        if matching_track is not None:
            Scheduler.defer(matching_track.restore_clip_color)
