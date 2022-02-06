from typing import TYPE_CHECKING, Any

from protocol0.domain.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, midi_clip, audio_clip, *a, **k):
        # type: (MidiClip, AudioClip, Any, Any) -> None
        properties = ["name"]
        if not isinstance(audio_clip.track, SimpleAudioTailTrack):
            properties += ["looping"]
            # not muted because we want to mute only midi clips

        if midi_clip.length == audio_clip.length:
            properties += ["loop_start", "loop_end", "start_marker", "end_marker"]

        # check we are not in the clip tail case
        if not audio_clip.is_recording and audio_clip.bar_length not in (midi_clip.bar_length, midi_clip.bar_length + 1):
            if not isinstance(audio_clip.track, SimpleAudioTailTrack):
                pass

        super(ClipSynchronizer, self).__init__(
            midi_clip,
            audio_clip,
            listenable_properties=properties,
            bidirectional=False,
            *a,
            **k
        )

    def is_syncable(self, clip):
        # type: (Clip) -> bool
        return not clip.track.is_recording and not SongFacade.record_mode

    def _sync_property(self, master, slave, property_name):
        # type: (Clip, Clip, str) -> None
        if not self.is_syncable(slave):
            return
        if property_name == "name":
            slave.clip_name.update(base_name=master.clip_name.base_name)
        else:
            super(ClipSynchronizer, self)._sync_property(master, slave, property_name)
