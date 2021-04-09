from a_protocol_0.components.actionManagers.AbstractActionManager import AbstractActionManager
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.utils.decorators import button_action


class ActionSetManager(AbstractActionManager):
    """
        This manager is supposed to group mundane tasks on Live like debug
        or one shot actions on a set (like upgrading to a new naming scheme)
    """
    def __init__(self, *a, **k):
        super(ActionSetManager, self).__init__(channel=14, *a, **k)
        # RACK encoder
        self.add_encoder(id=1,
                         on_press=self.action_update_racks)

        # CLIP encoder
        self.add_encoder(id=2,
                         on_press=self.action_set_clip_names)

        # TRAcK encoder
        self.add_encoder(id=3,
                         on_press=self.action_set_track_names)

        # LOG encoder
        self.add_encoder(id=13,
                         on_press=self.action_log_set)

    @button_action()
    def action_update_racks(self):
        for track in self.song.simple_tracks:
            [self.parent.deviceManager.update_rack(rack_device=device._device) for device in track.all_devices if isinstance(device, RackDevice)]

    @button_action()
    def action_set_clip_names(self):
        for clip in self.song.clips:
            clip.clip_name._base_name = ""
            clip.clip_name.update()

    @button_action()
    def action_set_track_names(self):
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

    @button_action()
    def action_log_set(self):
        return self.parent.logManager.log_set()