from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList
from a_protocol_0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack


class ActionGroupSet(AbstractActionGroup):
    """
    This manager is supposed to group mundane tasks on Live like debug
    or one shot actions on a set (like upgrading to a new naming scheme)
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=14, filter_active_tracks=False, *a, **k)
        # LOG encoder
        self.add_encoder(id=1, name="log", on_press=self.parent.logManager.log_set)

        # RACK encoder
        self.add_encoder(id=2, name="racks", on_press=self.update_racks)

        # CLIP encoder
        self.add_encoder(id=3, name="clips", on_press=self.set_clip_names)

        # TRAcK encoder
        self.add_encoder(id=4, name="tracks", on_press=self.set_track_appearance)

        # CHeCK encoder
        self.add_encoder(id=5, name="check", on_press=self.check_set)

    def update_racks(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            [
                self.parent.deviceManager.update_rack(rack_device=device._device)
                for device in track.all_devices
                if isinstance(device, RackDevice)
            ]

    def set_clip_names(self):
        # type: () -> None
        for clip in (clip for track in self.song.simple_tracks for clip in track.clips):
            clip.clip_name.update()

    def set_track_appearance(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            track.track_name.update()

        for track in AbstractTrackList(self.song.abstract_tracks).abstract_group_tracks:
            track.track_name.update()
            if track.instrument:
                track.color = track.instrument.TRACK_COLOR

        for track in self.song.abstract_tracks:
            if isinstance(track, SimpleGroupTrack):
                track.change_appearance_to_sub_tracks_instrument()

    def check_set(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_audio and not simple_track.is_armable:
                self.parent.log_error("Check the input routing of %s" % simple_track)

        self.set_clip_names()
        self.set_track_appearance()
        self.parent.show_message("Set checked !")
