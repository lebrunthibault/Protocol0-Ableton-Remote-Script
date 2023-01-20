from functools import partial

from typing import List, Optional, TYPE_CHECKING, Iterator

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class SimpleAudioTrackClips(object):
    def __init__(self, clip_infos):
        # type: (List["ClipInfo"]) -> None
        self._clip_infos = clip_infos

    def __repr__(self):
        # type: () -> str
        return "SimpleAudioTrackClips(\n%s\n)" % "\n".join([str(c) for c in self._clip_infos])

    def __iter__(self):
        # type: () -> Iterator[ClipInfo]
        return iter(self._clip_infos)

    @classmethod
    def make_from_track(cls, track):
        # type: (SimpleAudioTrack) -> SimpleAudioTrackClips
        return cls([ClipInfo(clip) for clip in track.clips if clip.midi_hash is not None])

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Sequence
        seq = Sequence()
        for clip_info in self._clip_infos:
            seq.add(partial(clip_info.broadcast_to_track, source_track, dest_track))

        seq.add(Backend.client().close_samples_windows)
        seq.add(
            lambda: Backend.client().show_success(
                "%s / %s clips replaced"
                % (sum(c.clips_replaced_count for c in self._clip_infos), len(source_track.clips))
            )
        )

        return seq.done()


class ClipInfo(object):
    def __init__(self, clip):
        # type: (AudioClip) -> None
        assert clip.midi_hash, "clip.midi_hash is None"
        self.index = clip.index
        self.name = clip.name
        self.midi_hash = clip.midi_hash
        self.clips_replaced_count = 0

    def __repr__(self):
        # type: () -> str
        # noinspection SpellCheckingInspection
        return "ClipInfo(\nname=%s,\nmidi_hash=%s)" % (
            self.name,
            self.midi_hash,
        )

    def _matches_clip_slot(self, clip_slot):
        # type: (AudioClipSlot) -> bool
        clip = clip_slot.clip

        return clip is not None and clip.midi_hash == self.midi_hash

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Optional[Sequence]
        source_cs = source_track.clip_slots[self.index]
        assert source_cs.clip is not None, "Couldn't find clip at index %s" % self.index

        matching_clip_slots = [cs for cs in dest_track.clip_slots if self._matches_clip_slot(cs)]

        seq = Sequence()
        for dest_cs in matching_clip_slots:
            source_track.replace_clip_sample(dest_track, dest_cs, source_cs)

        self.clips_replaced_count += len(matching_clip_slots)

        return seq.done()
