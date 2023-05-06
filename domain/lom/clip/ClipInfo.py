from functools import partial
from os.path import basename

from typing import TYPE_CHECKING, List, Dict, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ClipInfo(object):
    _DEBUG = False

    def __init__(self, clip, device_parameters, duplicate_clips=None):
        # type: (Clip, List[DeviceParameter], Optional[List[Clip]]) -> None
        duplicate_clips = duplicate_clips or []

        self.index = clip.index
        self.name = clip.name
        self.hash = clip.get_hash(device_parameters)
        self._duplicate_indexes = [clip.index for clip in duplicate_clips]

        self.replaced_clip_slots = []  # type: List[AudioClipSlot]

    def __repr__(self):
        # type: () -> str
        return "ClipInfo(name=%s,hash=%s,duplicates=%s)" % (
            self.name,
            self.hash,
            self._duplicate_indexes,
        )

    @classmethod
    def create_from_clips(cls, clips, device_parameters, clean_duplicates=False):
        # type: (List[Clip], List[DeviceParameter], bool) -> List["ClipInfo"]
        unique_clips_by_hash = {}  # type: Dict[float, List[Clip]]

        for clip in clips:
            clip_hash = clip.get_hash(device_parameters)
            unique_clips_by_hash[clip_hash] = unique_clips_by_hash.get(clip_hash, []) + [clip]

        clip_infos = [cls(clips[0], device_parameters, clips[1:]) for clips in unique_clips_by_hash.values()]

        if clean_duplicates:
            for clips in unique_clips_by_hash.values():
                for clip in clips[1:]:
                    clip.delete()

        return clip_infos

    def get_clips(self, clips):
        # type: (List[Clip]) -> List[Clip]
        clip_indexes = [self.index] + self._duplicate_indexes

        return [clip for clip in clips if clip.index in clip_indexes]

    def already_bounced_to(self, track):
        # type: (SimpleAudioTrack) -> bool
        return len(self.matching_clip_slots(track, exact=True)) > 0

    def matching_clip_slots(self, track, exact=False):
        # type: (SimpleAudioTrack, bool) -> List[AudioClipSlot]
        def matches_clip_slot(dest_track, dest_cs, exact_match):
            # type: (SimpleAudioTrack, AudioClipSlot, bool) -> bool
            dest_clip = dest_cs.clip

            if dest_clip is None:
                return False

            clip_mapping = dest_track.clip_mapping

            if self._DEBUG:
                hashes = clip_mapping._file_path_mapping.get(dest_clip.file_path, None)
                Logger.info("Comparing %s to %s : (%s, %s)" % (self, dest_cs, basename(dest_clip.file_path), hashes))


            return clip_mapping.path_matches_hash(dest_clip.file_path, self.hash, exact_match)


        return [cs for cs in track.clip_slots if matches_clip_slot(track, cs, exact_match=exact)]



    @classmethod
    def restore_duplicate_clips(cls, clip_infos):
        # type: (List["ClipInfo"]) -> Sequence
        seq = Sequence()
        for clip_info in clip_infos:
            seq.add(partial(clip_info.restore_duplicates, Song.selected_track()))

        return seq.done()

    def restore_duplicates(self, track):
        # type: (SimpleTrack) -> Sequence
        """Restore duplicates removed before flattening"""
        source_cs = track.clip_slots[self.index]

        assert source_cs.clip is not None, "restore duplicates : no clip at index %s" % self.index

        seq = Sequence()
        seq.add(
            [
                partial(source_cs.duplicate_clip_to, track.clip_slots[index])
                for index in self._duplicate_indexes
            ]
        )

        return seq.done()
