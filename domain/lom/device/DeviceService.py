from collections import Callable
from functools import partial

from typing import Dict, Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.utils import find_if, scroll_values
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    def __init__(self, browser_service, select_device):
        # type: (BrowserServiceInterface, Callable) -> None
        self._browser_service = browser_service
        self._select_device = select_device

    def update_audio_effect_rack(self, track, device):
        # type: (SimpleTrack, RackDevice) -> Sequence
        """ update rack with the version stored in browser, keeping old values for identical parameters """
        Logger.info("selecting and updating device %s (track %s)" % (device, track))
        parameters = {param.name: param.value for param in device.parameters if "macro" not in param.name.lower()}
        seq = Sequence()
        seq.add(partial(self._select_device, track, device))
        seq.add(partial(self._browser_service.update_audio_effect_preset, track, device))
        seq.add(partial(self._update_device_params, track, device.name, parameters))
        return seq.done()

    def _update_device_params(self, track, device_name, parameters):
        # type: (SimpleTrack, str, Dict[str, float]) -> None
        device = find_if(lambda d: d.name == device_name, list(track.devices))
        if not device:
            Logger.error("Couldn't find device with name %s in %s" % (device_name, track))
        for param_name, param_value in parameters.items():
            device.update_param_value(param_name=param_name, param_value=param_value)

    def load_device(self, device_name):
        # type: (str) -> Sequence
        device_enum = DeviceEnum.from_value(device_name.upper())  # type: DeviceEnum
        track = SongFacade.current_track().base_track
        Logger.dev(track)
        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))
        return seq.done()

    def show_or_load_device(self, device_name):
        # type: (str) -> Optional[Sequence]
        device_enum = DeviceEnum.from_value(device_name.upper())  # type: DeviceEnum
        track = SongFacade.current_track().base_track
        devices = track.devices.get_from_enum(device_enum)
        if len(devices) == 0:
            return self.load_device(device_name)

        if track.devices.selected in devices and SongFacade.selected_track() != track:
            next_device = track.devices.selected
        else:
            next_device = scroll_values(devices, track.devices.selected, True)

        self._select_device(track, next_device)
