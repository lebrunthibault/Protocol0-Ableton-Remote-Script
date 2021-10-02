from typing import Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.utils.decorators import p0_subject_slot


class MixingManager(AbstractControlSurfaceComponent):
    MIXING_PLUGIN_NAMES = ("ozone", "limiter")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MixingManager, self).__init__(*a, **k)
        self._master_track_output_meter_level_listener.subject = self.song._song.master_track

    @property
    def should_activate_mix_volume_follower(self):
        # type: () -> bool
        """ deprecated """
        return False
        if not self.song.is_playing:
            return False
        for device in self.song.master_track.all_devices:
            if any([name.lower() in device.name.lower() for name in self.MIXING_PLUGIN_NAMES]) and device.is_active:
                return False

        return True

    @p0_subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        # type: () -> None
        if not self.song.master_track or not self.should_activate_mix_volume_follower:
            return
        if self.song.master_track.output_meter_level >= 0.87:
            for track in self.song.abstract_tracks:  # type: AbstractTrack
                if not track.group_track:
                    track.volume *= 0.95
