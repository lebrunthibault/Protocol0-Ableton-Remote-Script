from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList
from a_protocol_0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack


class SetFixerManager(AbstractControlSurfaceComponent):
    """ Do audit and fix operations on a set """

    def check_set(self):
        # type: () -> None
        """ Checks the set is operational """
        for simple_track in self.song.simple_tracks:
            if simple_track.is_audio and not simple_track.is_armable:
                self.parent.log_error("Check the input routing of %s" % simple_track)

        self.parent.show_message("Set checked !")

    def fix_set(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""

        self._fix_tracks_appearance()
        self._fix_clips_appearance()
        self.parent.show_message("Set fixed !")

    def _fix_clips_appearance(self):
        # type: () -> None
        for clip in (clip for track in self.song.simple_tracks for clip in track.clips):
            clip.refresh_appearance()

    def _fix_tracks_appearance(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            track.refresh_appearance()

        for track in AbstractTrackList(self.song.abstract_tracks).abstract_group_tracks:
            track.refresh_appearance()

        for track in reversed(list(self.song.abstract_tracks)):
            if isinstance(track, SimpleGroupTrack):
                track.refresh_appearance()

    def _update_racks(self):
        # type: () -> None
        """ not used atm """
        for track in self.song.simple_tracks:
            [
                self.parent.deviceManager.update_rack(rack_device=device._device)
                for device in track.all_devices
                if isinstance(device, RackDevice)
            ]
