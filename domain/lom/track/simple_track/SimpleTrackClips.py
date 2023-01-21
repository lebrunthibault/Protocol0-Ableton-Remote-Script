from functools import partial

from typing import List, Optional, TYPE_CHECKING, Iterator, cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleTrackClips(object):
    def __init__(self, clip_infos):
        # type: (List["ClipInfo"]) -> None
        self._clip_infos = clip_infos

    def __repr__(self):
        # type: () -> str
        return "SimpleTrackClips(\n%s\n)" % "\n".join([str(c) for c in self._clip_infos])

    def __iter__(self):
        # type: () -> Iterator[ClipInfo]
        return iter(self._clip_infos)

    @classmethod
    def make_from_track(cls, track):
        # type: (SimpleTrack) -> SimpleTrackClips
        return cls([ClipInfo(clip) for clip in track.clips])

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Sequence
        seq = Sequence()

        for clip_info in self._clip_infos:
            seq.add(partial(clip_info.broadcast_to_track, source_track, dest_track))

        seq.add(
            lambda: Backend.client().show_success(
                "%s / %s clips replaced"
                % (sum(c.clips_replaced_count for c in self._clip_infos), len(dest_track.clips))
            )
        )

        return seq.done()

    def hydrate(self, clips):
        # type: (List[Clip]) -> None
        assert len(clips) == len(
            self._clip_infos
        ), "length mismatch between audio clips: len(clips) == %s, len(clip_infos) == %s" % (
            len(clips),
            len(self._clip_infos),
        )
        for clip, clip_info in zip(clips, self._clip_infos):
            clip.loop.update_from_dict(clip_info.loop_data)
            clip.looping = True


class ClipInfo(object):
    def __init__(self, clip):
        # type: (Clip) -> None
        self.index = clip.index
        self.name = clip.name
        self.loop_data = clip.loop.to_dict()
        self.clips_replaced_count = 0
        self.midi_hash = getattr(clip, "hash", None)  # type: Optional[int]
        self.file_path = getattr(clip, "file_path", None)  # type: Optional[str]

    def __repr__(self):
        # type: () -> str
        return "ClipInfo(\nname=%s)" % self.name

    def _matches_clip_slot(self, source_track, dest_track, dest_cs):
        # type: (SimpleAudioTrack, SimpleAudioTrack, AudioClipSlot) -> bool
        clip = dest_cs.clip
        if clip is None:
            return False

        src_midi_hash = self.midi_hash or source_track.file_path_mapping.get(
            cast(str, self.file_path), None
        )
        dest_midi_hash = dest_track.file_path_mapping.get(clip.file_path, None)

        return src_midi_hash is not None and src_midi_hash == dest_midi_hash

    def get_midi_hash(self, source_track):
        # type: (SimpleTrack) -> int
        if self.midi_hash is not None:
            return self.midi_hash
        else:
            return source_track.file_path_mapping.get(self.file_path)  # noqa

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Optional[Sequence]
        source_cs = source_track.clip_slots[self.index]
        assert source_cs.clip is not None, "Couldn't find clip at index %s" % self.index

        matching_clip_slots = [
            cs
            for cs in dest_track.clip_slots
            if self._matches_clip_slot(source_track, dest_track, cs)
        ]

        seq = Sequence()
        for dest_cs in matching_clip_slots:
            seq.add(partial(source_track.replace_clip_sample, dest_track, dest_cs, source_cs))

        seq.add(Backend.client().close_samples_windows)

        self.clips_replaced_count += len(matching_clip_slots)

        return seq.done()
