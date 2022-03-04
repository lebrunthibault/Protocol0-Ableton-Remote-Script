from protocol0.domain.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, midi_clip, audio_clip):
        # type: (MidiClip, AudioClip) -> None
        properties = ["name", "looping", "loop_start", "loop_end", "start_marker", "end_marker"]
        super(ClipSynchronizer, self).__init__(midi_clip, audio_clip, properties)

    def _sync_property(self, master, slave, property_name):
        # type: (Clip, Clip, str) -> None
        if not slave.is_syncable:
            return
        if property_name == "name":
            slave.clip_name.update(base_name=master.clip_name.base_name)
        elif master.loop.end != slave.loop.end and master.length > slave.length:
            # do not synchronize when duplicating midi loop or editing midi clip length manually
            return
        # following is when clips have same length but markers are offset
        elif property_name in ("loop_start", "start_marker") and master.loop.end != slave.loop.end:
            return
        elif property_name in ("loop_end", "end_marker") and master.loop.start != slave.loop.start:
            return
        else:
            super(ClipSynchronizer, self)._sync_property(master, slave, property_name)
