from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class MixingManager(AbstractControlSurfaceComponent):
    MIXING_PLUGIN_NAMES = ("ozone", "limiter")

    def __init__(self, *a, **k):
        super(MixingManager, self).__init__(*a, **k)
        self._master_track_output_meter_level_listener.subject = self.song.master_track

    @property
    def should_activate_mix_volume_follower(self):
        for device in self.song.master_track.devices:
            if any([name.lower() in device.name.lower() for name in self.MIXING_PLUGIN_NAMES]) and device.is_active:
                return True

        return False

    @subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        if self.should_activate_mix_volume_follower:
            return
        if self.song.master_track.output_meter_level >= 0.87:
            for track in self.song.root_tracks:
                track.volume *= 0.95
