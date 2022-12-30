from functools import partial

from typing import List, cast, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

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
        matching_track = find_if(
            lambda t: t != self and t.name == self.name, SongFacade.simple_tracks()
        )
        if matching_track is not None:
            matching_track.select()
            raise Protocol0Warning("Track already loaded")

        track_color = self.color
        self.focus()
        seq = Sequence()
        seq.add(Backend.client().drag_matching_track)
        seq.wait_for_backend_event("track_focused")
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("matching_track_loaded")
        return seq.done()
