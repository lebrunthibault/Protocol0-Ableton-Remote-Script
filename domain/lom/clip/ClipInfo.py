from typing import TYPE_CHECKING, cast, List

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ClipInfo(object):
    def __init__(self, clip):
        # type: (Clip) -> None
        self.index = clip.index
        self.name = clip.name
        self.midi_hash = None
        self.file_path = None
        if isinstance(clip, MidiClip):
            self.midi_hash = clip.midi_hash
        elif isinstance(clip, AudioClip):
            self.file_path = clip.file_path
        self.replaced_clip_slots = []  # type: List[AudioClipSlot]

    def __repr__(self):
        # type: () -> str
        return "ClipInfo(name=%s)" % self.name

    def matches_clip_slot(self, dest_track, dest_cs):
        # type: (SimpleAudioTrack, AudioClipSlot) -> bool
        dest_clip = dest_cs.clip
        if dest_clip is None:
            return False

        if self.midi_hash is not None:
            return dest_track.audio_to_midi_clip_mapping.hash_matches_file_path(
                self.midi_hash, dest_clip.file_path
            )
        else:
            return dest_track.audio_to_midi_clip_mapping.file_path_matches_file_path(
                cast(str, self.file_path), dest_clip.file_path
            )
