from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class MixingManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(MixingManager, self).__init__(*a, **k)
        self._master_track_output_meter_level_listener.subject = self.song.master_track

    @subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        if self.song.master_track.output_meter_level >= 0.87:
            for track in self.song.root_tracks:
                track.volume *= 0.95
