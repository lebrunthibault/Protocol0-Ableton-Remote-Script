from functools import partial

from typing import Iterator, List, Dict, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.Device import Device
from protocol0.lom.device.PluginDevice import PluginDevice
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
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
                if any(enum.matches_device(device) for enum in DeviceEnum.updatable_devices()):
                    seq.add(partial(self.parent.deviceManager.update_audio_effect_rack, device=device))

        return seq.done()

    def delete_unnecessary_devices(self, full_scan=False):
        # type: (bool) -> None
        devices_to_delete = list(self.get_deletable_devices(full_scan=full_scan))
        if len(devices_to_delete) == 0:
            if full_scan is False:
                self.delete_unnecessary_devices(full_scan=True)
            else:
                self.parent.show_message("No devices to delete")
            return

        devices_by_name = {}  # type: Dict[str, List[Device]]
        for device in devices_to_delete:
            name = device.name or device.class_name
            if name not in devices_by_name:
                devices_by_name[name] = []
            devices_by_name[name].append(device)

        info = "\n".join(("%s %s" % (len(devices), cls) for cls, devices in devices_by_name.items()))

        seq = Sequence()
        seq.prompt("%s devices to delete,\n\n%s\n\nproceed ?" % (len(devices_to_delete), info))
        seq.add([device.delete for device in devices_to_delete])
        seq.add(lambda: self.parent.show_message("Devices deleted"))
        seq.add(self.delete_unnecessary_devices)  # now delete enclosing racks if empty
        seq.done()

    def get_deletable_devices(self, full_scan):
        # type: (bool) -> Iterator[Device]
        tracks = [track for track in self.song.simple_tracks if not isinstance(track, SimpleDummyTrack)]

        # devices off
        for device_enum in DeviceEnum.deprecated_devices():
            for track in tracks:
                device = track.get_device_from_enum(device_enum)
                if device:
                    yield device

        # devices with default values (unchanged)
        for device_enum in DeviceEnum:  # type: DeviceEnum  # type: ignore[no-redef]
            try:
                default_parameter_values = device_enum.main_parameters_default
            except Protocol0Error:
                continue

            for track in tracks:
                device = track.get_device_from_enum(device_enum)
                if not device:
                    continue
                device_on = device.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON)
                if device_on.value is False and not device_on.is_automated:
                    yield device
                if all([parameter_value.matches(device) for parameter_value in default_parameter_values]):
                    yield device

        # empty mix racks
        for track in self.song.simple_tracks:
            mix_rack = track.get_device_from_enum(DeviceEnum.MIX_RACK)  # type: Optional[RackDevice]
            if mix_rack and len(mix_rack.chains[0].devices) == 0:
                yield mix_rack

        if not full_scan:
            return

        # plugin devices
        white_list_names = [d.device_name for d in DeviceEnum.plugin_white_list()]
        for track in self.song.simple_tracks:
            for device in track.all_devices:
                if isinstance(device, PluginDevice) and device.name not in white_list_names:
                    yield device
