from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.utils.decorators import button_action


class ActionSetManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(ActionSetManager, self).__init__(*a, **k)
        # RACK encoder
        MultiEncoder(channel=14, identifier=1,
                     on_press=self.action_update_racks)

    @button_action()
    def action_update_racks(self):
        for track in self.song.tracks:
            [self.parent.deviceManager.update_rack(rack_device=device._device) for device in track.all_devices if isinstance(device, RackDevice)]
