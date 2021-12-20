from typing import TYPE_CHECKING, Any

from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.utils.log import log_ableton

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, midi_clip, audio_clip, no_muted, *a, **k):
        # type: (MidiClip, AudioClip, bool, Any, Any) -> None
        properties = ["name"]
        if not no_muted:
            properties.append("muted")

        if midi_clip.length == audio_clip.length and not midi_clip.track.abstract_track.record_clip_tails:
            properties += ["loop_start", "loop_end", "start_marker", "end_marker"]

        # check we are not in the clip tail case
        if not audio_clip.is_recording and audio_clip.bar_length not in (midi_clip.bar_length, midi_clip.bar_length + 1):
            if not isinstance(audio_clip.track, SimpleAudioTailTrack):
                log_ableton(  # type: ignore[unreachable]
                    "Inconsistent clip lengths for clip %s of track %s (audio is %s, midi is %s)" % (
                        audio_clip, audio_clip.track.abstract_track, audio_clip.bar_length, midi_clip.bar_length),
                    level=LogLevelEnum.WARNING)

        super(ClipSynchronizer, self).__init__(
            midi_clip,
            audio_clip,
            listenable_properties=properties,
            *a,
            **k
        )

    def is_syncable(self, clip):
        # type: (Clip) -> bool
        return not clip.track.is_recording

    def _sync_property(self, master, slave, property_name):
        # type: (Clip, Clip, str) -> None
        if not self.is_syncable(slave):
            return
        if property_name == "name":
            slave.clip_name.update(base_name=master.clip_name.base_name)
        else:
            super(ClipSynchronizer, self)._sync_property(master, slave, property_name)
