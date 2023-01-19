from functools import partial
from os.path import basename

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
        return cls([ClipInfo(clip) for clip in track.clips])

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Sequence
        seq = Sequence()
        for clip_info in self._clip_infos:
            seq.add(partial(clip_info.broadcast_to_track, source_track, dest_track))

        seq.add(partial(Backend.client().close_explorer_window, "Recorded"))
        seq.add(
            lambda: Backend.client().show_success(
                "%s clips replaced (from %s clips)"
                % (sum(c.clips_replaced_count for c in self._clip_infos), len(self._clip_infos))
            )
        )

        return seq.done()

    def hydrate(self, clips):
        # type: (List[AudioClip]) -> None
        assert len(clips) == len(self._clip_infos), "length mismatch between audio clips"
        for clip, clip_info in zip(clips, self._clip_infos):
            clip.name = clip_info.name


class ClipInfo(object):
    def __init__(self, clip):
        # type: (AudioClip) -> None
        self.index = clip.index
        self.name = clip.name
        self.midi_hash = clip.midi_hash
        self._file_path = clip.file_path
        self._loop_data = clip.loop.to_dict()
        self.clips_replaced_count = 0

    def __repr__(self):
        # type: () -> str
        return "ClipInfo(\nname=%s,\nfile_path=%s,\nloop_data=%s)" % (
            self.name,
            basename(self._file_path),
            self._loop_data,
        )

    def _matches_clip_slot(self, clip_slot):
        # type: (AudioClipSlot) -> bool
        clip = clip_slot.clip
        return (
            clip is not None
            and clip.midi_hash == self.midi_hash
        )

    def broadcast_to_track(self, source_track, dest_track):
        # type: (SimpleAudioTrack, SimpleAudioTrack) -> Optional[Sequence]
        source_cs = source_track.clip_slots[self.index]
        assert source_cs.clip is not None, "Couldn't find clip at index %s" % self.index

        matching_clip_slots = [cs for cs in dest_track.clip_slots if self._matches_clip_slot(cs)]

        from protocol0.shared.logging.Logger import Logger
        Logger.dev((source_track, dest_track))
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(source_cs.clip)
        Logger.dev(matching_clip_slots)

        seq = Sequence()
        for clip_slot in matching_clip_slots:
            from protocol0.shared.logging.Logger import Logger
            Logger.dev((clip_slot, clip_slot.clip))
            device_params = dest_track.devices.parameters  # type: ignore[has-type]
            automated_params = clip_slot.clip.automation.get_automated_parameters(device_params)

            # duplicate when no automation else manual action is needed
            if len(automated_params) == 0:
                clip_slot.replace_clip_sample(source_cs)
            else:
                seq.add(partial(clip_slot.replace_clip_sample, None, self._file_path))

            self.clips_replaced_count += 1

        return seq.done()
