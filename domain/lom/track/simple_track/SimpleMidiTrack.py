from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[MidiClipSlot]
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # noqa

    def has_same_clips(self, track):
        # type: (AbstractTrack) -> bool
        if not isinstance(track, SimpleMidiTrack):
            return False

        if len(self.clips) != len(track.clips):
            return False

        for index, clip in enumerate(self.clips):
            other_clip = track.clips[index]

            if clip.hash() != other_clip.hash():
                return False

        return True
