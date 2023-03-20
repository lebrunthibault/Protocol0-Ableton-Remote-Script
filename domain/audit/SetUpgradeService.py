from functools import partial

from typing import Iterator, List, Dict, Tuple

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class SetUpgradeService(object):
    def __init__(self, validator_service, track_crud_component):
        # type: (ValidatorService, TrackCrudComponent) -> None
        self._validator_service = validator_service
        self._track_crud_component = track_crud_component

    def delete_unnecessary_devices(self, full_scan=False):
        # type: (bool) -> None
        devices_to_delete = list(self.get_deletable_devices())
        if len(devices_to_delete) == 0:
            if full_scan is False:
                self.delete_unnecessary_devices(full_scan=True)
            else:
                StatusBar.show_message("No devices to delete")
            return

        devices_by_name = {}  # type: Dict[str, List[Device]]
        for track, device in devices_to_delete:
            name = device.name or device.class_name
            if name not in devices_by_name:
                devices_by_name[name] = []
            devices_by_name[name].append(device)

        info = "\n".join(
            ("%s %s" % (len(devices), cls) for cls, devices in devices_by_name.items())
        )

        seq = Sequence()
        seq.prompt("%s devices to delete,\n\n%s\n\nProceed ?" % (len(devices_to_delete), info))
        seq.add([partial(track.devices.delete, device) for track, device in devices_to_delete])
        seq.add(lambda: StatusBar.show_message("Devices deleted"))
        seq.add(self.delete_unnecessary_devices)  # now delete enclosing racks if empty
        seq.done()

    def get_deletable_devices(self):
        # type: () -> Iterator[Tuple[SimpleTrack, Device]]
        # devices with default values (unchanged)
        for device_enum in DeviceEnum:  # type: DeviceEnum
            try:
                default_parameter_values = device_enum.main_parameters_default
            except Protocol0Error:
                continue

            for track in Song.all_simple_tracks():
                device = track.devices.get_one_from_enum(device_enum)
                if not device:
                    continue
                device_on = device.get_parameter_by_name(DeviceParameterEnum.DEVICE_ON)
                if device_on.value is False and not device_on.is_automated:
                    yield track, device
                if all(
                    [
                        parameter_value.matches(device)
                        for parameter_value in default_parameter_values
                    ]
                ):
                    yield track, device
