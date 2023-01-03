from functools import partial

from typing import List, cast, Any

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiMatchingTrack import SimpleMidiMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiTrack, self).__init__(*a, **k)
        self.matching_track = SimpleMidiMatchingTrack(self)
        self.arm_state.register_observer(self.matching_track)

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

        return len(self.clips) == len(track.clips) and all(
            clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips)
        )

    def duplicate_selected_clip(self):
        # type: () -> Sequence
        selected_cs = SongFacade.selected_clip_slot(MidiClipSlot)
        clip = selected_cs.clip
        if clip is None:
            raise Protocol0Warning("No selected clip")

        matching_clip_slots = [
            c for c in self.clip_slots if c.clip and c.clip.matches(clip) and c.clip is not clip
        ]

        Backend.client().show_info("Copying to %s clips" % len(matching_clip_slots))
        seq = Sequence()
        seq.add([partial(selected_cs.duplicate_clip_to, cs) for cs in matching_clip_slots])
        return seq.done()

    def flatten(self):
        # type: () -> Sequence
        # this is needed to have flattened clip of the right length
        SongFacade._live_song().stop_playing()
        for clip in self.clips:
            clip.looping = False

        track_color = self.color

        seq = Sequence()
        seq.add(self.focus)
        seq.defer()
        seq.add(Backend.client().flatten_track)
        seq.wait_for_backend_event("track_focused")
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("track_flattened")
        seq.add(lambda: SongFacade.selected_track(SimpleAudioTrack).post_flatten())
        return seq.done()

    def disconnect(self):
        # type: () -> None
        super(SimpleMidiTrack, self).disconnect()

        self.matching_track.disconnect()
