from functools import partial

from typing import Iterator, List, Dict, Type, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.Device import Device
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import prompt


class SetUpgradeManager(AbstractControlSurfaceComponent):
    @prompt("Update updatable racks ?")
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
        devices_to_delete = list(self._get_devices_to_delete())
        if len(devices_to_delete) == 0:
            self.parent.show_message("No devices to delete")
            return

        devices_by_name = {}  # type: Dict[str, List[Device]]
        for device in devices_to_delete:
            name = device.name
            if name not in devices_by_name:
                devices_by_name[name] = []
            devices_by_name[name].append(device)

        info = "\n".join(("%s %s" % (len(devices), cls) for cls, devices in devices_by_name.items()))

        seq = Sequence()
        seq.add(partial(self.system.prompt, "%s devices to delete,\n\n%s\n\nproceed ?" % (len(devices_to_delete), info)), wait_for_system=True)
        seq.add([device.delete for device in devices_to_delete])
        seq.add(lambda: self.parent.show_message("Devices deleted"))
        seq.add(self.delete_unnecessary_devices)  # now delete enclosing racks if empty
        seq.done()

    def _get_devices_to_delete(self):
        # type: () -> Iterator[Device]
        for device_enum in DeviceEnum:  # type: DeviceEnum
            try:
                default_parameter_values = device_enum.main_parameters_default
            except Protocol0Error:
                continue

            for track in self.song.simple_tracks:
                device = track.get_device_from_enum(device_enum)
                self.parent.log_dev("%s -> %s" % (device_enum, device))
                if not device:
                    continue
                if all([parameter_value.matches(device) for parameter_value in default_parameter_values]):
                    yield device

        for track in self.song.simple_tracks:
            mix_rack = track.get_device_from_enum(DeviceEnum.MIX_RACK)  # type: Optional[RackDevice]
            if mix_rack and len(mix_rack.chains[0].devices) == 0:
                yield mix_rack
