from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.lom.device.RackDevice import RackDevice


class ActionGroupSet(AbstractActionGroup):
    """
    This manager is supposed to group mundane tasks on Live like debug
    or one shot actions on a set (like upgrading to a new naming scheme)
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=14, *a, **k)
        # LOG encoder
        self.add_encoder(id=1, name="log", on_press=self.parent.logManager.log_set)

        # RACK encoder
        self.add_encoder(id=2, name="racks", on_press=self.update_racks)

        # CLIP encoder
        self.add_encoder(id=3, name="clips", on_press=self.set_clip_names)

        # TRAcK encoder
        self.add_encoder(id=4, name="tracks", on_press=self.set_track_names)

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
        for clip in self.song.clips:
            clip.clip_name.update()

    def set_track_names(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            # previous automation track naming
            if "_auto" in track.name:
                try:
                    [parameter_name, device_name, device_type, _] = track.name.split(":")
                except ValueError:
                    continue

                track.name = "_%s" % parameter_name
            else:
                track.track_name.update()
