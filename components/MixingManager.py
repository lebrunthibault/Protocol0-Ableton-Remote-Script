from typing import Any

from _Framework.SubjectSlot import subject_slot_group
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.config import Config
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.utils.decorators import p0_subject_slot


class MixingManager(AbstractControlSurfaceComponent):
    MIXING_PLUGIN_NAMES = ("ozone", "limiter")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MixingManager, self).__init__(*a, **k)
        self._master_track_output_meter_level_listener.subject = self.song._song.master_track

    def toggle_volume_check(self):
        # type: () -> None
        Config.VOLUME_LISTENER_ACTIVE = not Config.VOLUME_LISTENER_ACTIVE
        self.parent.show_message("VOLUME_LISTENER_ACTIVE: %s" % Config.VOLUME_LISTENER_ACTIVE)
        listenable_tracks = self.song._song.tracks
        if not Config.VOLUME_LISTENER_ACTIVE:
            listenable_tracks = []
        self._track_output_meter_level_listener.replace_subjects(listenable_tracks)

    @property
    def _should_activate_mix_volume_follower(self):
        # type: () -> bool
        """ deprecated """
        if not Config.VOLUME_LISTENER_ACTIVE:
            return False
        for device in self.song.master_track.all_devices:
            if any([name.lower() in device.name.lower() for name in self.MIXING_PLUGIN_NAMES]) and device.is_active:
                return False

        return True

    @p0_subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        # type: () -> None
        if not self.song.master_track or not self._should_activate_mix_volume_follower:
            return
        if self.song.master_track.output_meter_level >= 0.87:
            for track in self.song.abstract_tracks:  # type: AbstractTrack
                if not track.group_track:
                    track.volume *= 0.95

    @subject_slot_group("output_meter_level")
    def _track_output_meter_level_listener(self, track):
        # type: (Live.Track.Track) -> None
        if track.output_meter_level < 0.91:
            return
        self.parent.log_error("%s is clipping" % track.name)
