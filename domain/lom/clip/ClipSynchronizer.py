from functools import partial

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class ClipSynchronizer(UseFrameworkEvents):
    """ For ExternalSynthTrack """

    def __init__(self, midi_clip, audio_clip):
        # type: (MidiClip, AudioClip) -> None
        super(ClipSynchronizer, self).__init__()
        properties = ["name", "looping", "loop_start", "loop_end", "start_marker", "end_marker"]

        master, slave = midi_clip, audio_clip
        lom_property_name = master.lom_property_name

        for property_name in properties:
            self.register_slot(getattr(master, lom_property_name),
                               partial(Scheduler.defer, partial(self._sync_property, master, slave, property_name)),
                               property_name)

    def _sync_property(self, master, slave, property_name):
        # type: (Clip, Clip, str) -> None
        if not slave.is_syncable:
            return
        if property_name == "name":
            slave.clip_name.update(base_name=master.clip_name.base_name)
        # following is when clips have same length but markers are offset
        elif property_name in ("loop_start", "start_marker") and master.loop.end != slave.loop.end:
            return
        elif property_name in ("loop_end", "end_marker") and master.loop.start != slave.loop.start:
            return
        else:
            master_value = getattr(master, property_name)
            slave_value = getattr(slave, property_name)

            if slave_value != master_value:
                setattr(slave, property_name, master_value)
