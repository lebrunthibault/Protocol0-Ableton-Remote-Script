from functools import partial

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.sequence.Sequence import Sequence


class SetUpgradeManager(AbstractControlSurfaceComponent):
    def update_audio_effect_racks(self):
        # type: () -> Sequence
        seq = Sequence()
        for track in self.song.simple_tracks:
            for device in track.all_devices:
                if not isinstance(device, RackDevice):
                    continue
                if any(enum.matches_device(device) for enum in DeviceEnum.updatable_device_enums()):
                    seq.add(partial(self.parent.deviceManager.update_audio_effect_rack, device=device))

        return seq.done()

    def delete_unnecessary_devices(self):
        # type: () -> None
        for device_enum in DeviceEnum:  # type: DeviceEnum
            try:
                device_parameter_enum, default_value = device_enum.main_parameter_default
                for track in self.song.simple_tracks:
                    device = track.get_device_from_enum(device_enum)
                    if not device:
                        return
                    device_main_parameter = device.get_parameter_by_name(device_parameter_name=device_parameter_enum)
                    if device_main_parameter.value == default_value:
                        track.delete_device(device=device)
            except Protocol0Error:
                continue
