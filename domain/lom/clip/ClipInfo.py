from os.path import basename

from typing import TYPE_CHECKING, cast, List

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ClipInfo(object):
    _DEBUG = True

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
        file_path = self.file_path and basename(self.file_path)

        return "ClipInfo(name=%s,midi_hash=%s,file_path=%s)" % (self.name, self.midi_hash, file_path)

    def already_bounced_to(self, track):
        # type: (SimpleAudioTrack) -> bool
        return any(self.matches_clip_slot(track, cs, False) for cs in track.clip_slots)

    def matches_clip_slot(self, dest_track, dest_cs, exclude_identity=True):
        # type: (SimpleAudioTrack, AudioClipSlot, bool) -> bool
        dest_clip = dest_cs.clip

        if dest_clip is None:
            return False

        if self._DEBUG:
            Logger.info("dest clip: %s -> %s" % (dest_clip, basename(dest_clip.file_path)))

        if self.midi_hash is not None:
            return dest_track.audio_to_midi_clip_mapping.hash_matches_file_path(
                self.midi_hash, dest_clip.file_path, exclude_identity
            )
        else:
            return dest_track.audio_to_midi_clip_mapping.file_path_updated_matches_file_path(
                cast(str, self.file_path), dest_clip.file_path,exclude_identity
            )
