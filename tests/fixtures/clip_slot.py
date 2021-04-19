import Live
from typing import Optional, Any, cast

from _Framework.SubjectSlot import Subject
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbletonClipSlot(Subject):
    __subject_events__ = ("has_clip", "is_triggered")

    def __init__(self, clip=None):
        # type: (Optional[Any]) -> None
        self.clip = clip
        self.has_clip = bool(clip)


def make_clip_slot(track, clip_length, clip_loop_start):
    # type: (SimpleTrack, float, float) -> ClipSlot
    from a_protocol_0.tests.fixtures.clip import AbletonClip

    return ClipSlot(
        clip_slot=cast(
            Live.ClipSlot.ClipSlot, AbletonClipSlot(AbletonClip(length=clip_length, loop_start=clip_loop_start))
        ),
        index=0,
        track=track,
    )
