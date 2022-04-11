from collections import Callable
from functools import partial

from typing import Optional, Tuple, Dict, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.PluginDeviceAddedEvent import PluginDeviceAddedEvent
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 830
    SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT = 992
    SHOW_HIDE_SAVABLE_PLUGIN_BUTTON_PIXEL_HEIGHT = 970
    COLLAPSED_DEVICE_PIXEL_WIDTH = 38
    COLLAPSED_RACK_DEVICE_PIXEL_WIDTH = 28
    WIDTH_PIXEL_OFFSET = 4

    def __init__(self, browser_service, select_device):
        # type: (BrowserServiceInterface, Callable) -> None
        self._browser_service = browser_service
        self._select_device = select_device
        DomainEventBus.subscribe(PluginDeviceAddedEvent, self._on_plugin_device_added_event)

    def _on_plugin_device_added_event(self, event):
        # type: (PluginDeviceAddedEvent) -> None
        if event.device not in SongFacade.selected_track().devices:
            return

        Scheduler.defer(partial(self.make_plugin_window_showable, SongFacade.selected_track(), event.device))

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

    def _get_device_click_x_position(self, device_position):
        # type: (int) -> int
        return self.WIDTH_PIXEL_OFFSET + device_position * self.COLLAPSED_DEVICE_PIXEL_WIDTH

    def make_plugin_window_showable(self, track, device):
        # type: (SimpleTrack, Device) -> Sequence
        """ handles only one level of grouping in racks. Should be enough for now """
        parent_rack = self._find_parent_rack(track, device)
        seq = Sequence()
        seq.add(ApplicationView.show_device)

        if not parent_rack:
            seq.add(partial(self._make_top_device_window_showable, track, device))
        else:
            seq.add(partial(self._make_nested_device_window_showable, track, device, parent_rack))

        return seq.done()

    def _make_top_device_window_showable(self, track, device):
        # type: (SimpleTrack, Device) -> Sequence
        devices_to_uncollapse = []  # type: List[Device]

        for d in track.devices:
            if not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True
        (x_device, y_device) = self._get_device_show_button_click_coordinates(track, device)
        seq = Sequence()
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_device, y=y_device, activate=True))
        seq.wait(6)
        seq.add(partial(self.uncollapse_devices, devices_to_uncollapse))

        return seq.done()

    def _make_nested_device_window_showable(self, track, device, parent_rack):
        # type: (SimpleTrack, Device, RackDevice) -> Sequence
        devices_to_uncollapse = []  # type: List[Device]

        for d in track.devices:
            if d != parent_rack and not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True
        for d in parent_rack.chains[0].devices:
            if not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True

        (x_rack, y_rack) = self._get_rack_show_macros_button_click_coordinates(track, parent_rack)
        (x_device, y_device) = self._get_device_show_button_click_coordinates(track, device, parent_rack)

        seq = Sequence()
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_rack, y=y_rack, activate=False))
        seq.wait(5)
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_device, y=y_device, activate=True))
        seq.wait(10)
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_rack, y=y_rack, activate=True))
        # at this point the rack macro controls could still be hidden if the plugin window masks the button
        seq.add(partial(self.uncollapse_devices, devices_to_uncollapse), name="restore device collapse state")

        return seq.done()

    def uncollapse_devices(self, devices_to_uncollapse):
        # type: (List[Device]) -> None
        for d in devices_to_uncollapse:
            d.is_collapsed = False

    def _get_device_show_button_click_coordinates(self, track, device, rack_device=None):
        # type: (SimpleTrack, Device, RackDevice) -> Tuple[int, int]
        """ one grouping level only : expects all devices to be folded and macro controls hidden """
        if device.name == DeviceEnum.REV2_EDITOR.device_name:
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT
        else:
            y = self.SHOW_HIDE_SAVABLE_PLUGIN_BUTTON_PIXEL_HEIGHT

        if not rack_device:
            device_position = list(track.devices).index(device) + 1
            x = self._get_device_click_x_position(device_position)
        else:
            device_position = list(rack_device.chains[0].devices).index(device) + 1
            (x_rack, _) = self._get_rack_show_macros_button_click_coordinates(track, rack_device)
            x = x_rack + device_position * self.COLLAPSED_RACK_DEVICE_PIXEL_WIDTH

        return x - 3, y - 2  # we click not exactly in the center so as to know if the button is activated or not

    def _get_rack_show_macros_button_click_coordinates(self, track, rack_device):
        # type: (SimpleTrack, Device) -> Tuple[int, int]
        """ top racks only : expects all devices to be folded """
        parent_rack_position = list(track.devices).index(rack_device) + 1
        x = self._get_device_click_x_position(parent_rack_position)
        y = self.SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT

        return x, y

    def _find_parent_rack(self, track, device):
        # type: (SimpleTrack, Device) -> Optional[RackDevice]
        if device in track.devices:
            return None

        for rack_device in [d for d in track.devices if isinstance(d, RackDevice)]:
            if device in rack_device.chains[0].devices:
                return rack_device

        raise Protocol0Error("Couldn't find device %s (may be too nested to be detected)" % device.name)
