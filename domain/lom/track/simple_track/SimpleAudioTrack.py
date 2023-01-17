from functools import partial

from typing import List, cast, Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioMatchingTrack import (
    SimpleAudioMatchingTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
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
        return super(SimpleAudioTrack, self).clips  # noqa

    def has_same_clips(self, track):
        # type: (SimpleAudioTrack) -> bool
        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def load_full_track(self):
        # type: () -> Sequence
        assert isinstance(Song.current_track(), SimpleAudioTrack), "Track already loaded"
        matching_track = find_if(
            lambda t: t != self and t.name == self.name and not t.is_foldable,
            Song.simple_tracks(),
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
        seq.add(partial(Backend.client().show_success, "I LOVE YOU <3"))
        return seq.done()
