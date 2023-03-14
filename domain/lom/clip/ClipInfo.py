from functools import partial
from os.path import basename

from typing import TYPE_CHECKING, List, Dict, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ClipInfo(object):
    _DEBUG = True

    def __init__(self, clip, duplicate_clips=None):
        # type: (Clip, Optional[List[Clip]]) -> None
        duplicate_clips = duplicate_clips or []

        self.index = clip.index
        self.name = clip.name
        self.midi_hash = None
        self.file_path = None
        if isinstance(clip, MidiClip):
            self.midi_hash = clip.midi_hash
        elif isinstance(clip, AudioClip):
            self.file_path = clip.file_path

        self._duplicate_indexes = [clip.index for clip in duplicate_clips]

        self.replaced_clip_slots = []  # type: List[AudioClipSlot]

    def __repr__(self):
        # type: () -> str
        file_path = self.file_path and basename(self.file_path)

        return "ClipInfo(name=%s,midi_hash=%s,file_path=%s,duplicates=%s)" % (
            self.name,
            self.midi_hash,
            file_path,
            self._duplicate_indexes,
        )

    @classmethod
    def create_from_clips(cls, clips, device_parameters, clean_duplicates=False):
        # type: (List[Clip], List[DeviceParameter], bool) -> List["ClipInfo"]
        unique_clips_by_hash = {}  # type: Dict[float, List[Clip]]

        for clip in clips:
            clip_hash = clip.get_hash(device_parameters)
            unique_clips_by_hash[clip_hash] = unique_clips_by_hash.get(clip_hash, []) + [clip]

        clip_infos = [cls(clips[0], clips[1:]) for clips in unique_clips_by_hash.values()]

        if clean_duplicates:
            for clips in unique_clips_by_hash.values():
                for clip in clips[1:]:
                    clip.delete()

        return clip_infos

    def get_clips(self, track):
        # type: (SimpleTrack) -> List[Clip]
        clip_indexes = [self.index] + self._duplicate_indexes

        return [track.clip_slots[index].clip for index in clip_indexes]

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

            if self._DEBUG:
                compare = "midi hash" if self.midi_hash is not None else "path"
                Logger.info("Comparing %s to %s using %s" % (self, dest_cs, compare))

            clip_mapping = dest_track.clip_mapping
            args = (dest_clip.file_path, exact_match)

            if self.midi_hash is not None:
                return clip_mapping.hash_matches_path(self.midi_hash, *args)
            else:
                assert self.file_path is not None, "file path is None"
                return clip_mapping.path_matches_path(self.file_path, *args)


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

        assert source_cs.clip is not None

        seq = Sequence()
        seq.add(
            [
                partial(source_cs.duplicate_clip_to, track.clip_slots[index])
                for index in self._duplicate_indexes
            ]
        )

        return seq.done()
