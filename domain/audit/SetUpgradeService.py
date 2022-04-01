from functools import partial

from typing import Iterator, List, Dict, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.shared.Config import Config
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar


class SetUpgradeService(object):
    def __init__(self, device_service, validator_service):
        # type: (DeviceService, ValidatorService) -> None
        self._device_service = device_service
        self._validator_service = validator_service

    def update_audio_effect_racks(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.prompt("Update updatable racks ?")
        for track in SongFacade.all_simple_tracks():
            for device in track.all_devices:
                if not isinstance(device, RackDevice):
                    continue
                if any(enum.matches_device(device) for enum in DeviceEnum.updatable_devices()):
                    seq.add(partial(self._device_service.update_audio_effect_rack, device=device))

        return seq.done()

    def update_external_synth_tracks_add_clip_tails(self):
        # type: () -> Optional[Sequence]
        tracks = []
        for track in SongFacade.abstract_tracks():
            if not isinstance(track, ExternalSynthTrack):
                continue
            if not track.audio_tail_track:
                tracks.append(track)

        if not all(self._validator_service.validate_object(track) for track in tracks):
            Logger.error("invalid ExternalSynthTrack(s)")
            return None

        seq = Sequence()
        seq.prompt("Add clip tail track to %s external synth tracks?" % len(tracks))
        for track in tracks:
            if track.audio_tail_track is None:
                track.is_folded = False
                seq.add(track.audio_track.duplicate)
                seq.wait(10)
        return seq.done()

    def delete_unnecessary_devices(self, full_scan=False):
        # type: (bool) -> None
        devices_to_delete = list(self.get_deletable_devices(full_scan=full_scan))
        if len(devices_to_delete) == 0:
            if full_scan is False:
                self.delete_unnecessary_devices(full_scan=True)
            else:
                StatusBar.show_message("No devices to delete")
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
        seq.add(lambda: StatusBar.show_message("Devices deleted"))
        seq.add(self.delete_unnecessary_devices)  # now delete enclosing racks if empty
        seq.done()

    def get_deletable_devices(self, full_scan):
        # type: (bool) -> Iterator[Device]
        tracks = [track for track in SongFacade.all_simple_tracks() if not isinstance(track, SimpleDummyTrack)]

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
        for track in SongFacade.all_simple_tracks():
            mix_rack = track.get_device_from_enum(DeviceEnum.MIX_RACK)  # type: Optional[RackDevice]
            if mix_rack and len(mix_rack.chains[0].devices) == 0:
                yield mix_rack

        if not full_scan:
            return

        # plugin devices
        if Config.CHECK_PLUGINS_TO_REMOVE:
            white_list_names = [d.device_name for d in DeviceEnum.plugin_white_list()]
            for track in SongFacade.all_simple_tracks():
                for device in track.all_devices:
                    if isinstance(device, PluginDevice) and device.name not in white_list_names:
                        yield device
