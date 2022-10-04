from functools import partial

from typing import Optional, Tuple, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.sequence.Sequence import Sequence


class DeviceDisplayService(object):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 830
    SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT = 992
    SHOW_HIDE_SAVABLE_PLUGIN_BUTTON_PIXEL_HEIGHT = 970
    COLLAPSED_DEVICE_PIXEL_WIDTH = 38
    COLLAPSED_RACK_DEVICE_PIXEL_WIDTH = 28
    CHAIN_MIXER_PIXEL_WIDTH = 325
    WIDTH_PIXEL_OFFSET = 4

    def __init__(self, browser_service):
        # type: (BrowserServiceInterface) -> None
        self._browser_service = browser_service

    def make_plugin_window_showable(self, track, device):
        # type: (SimpleTrack, Device) -> Sequence
        """handles only one level of grouping in racks. Should be enough for now"""
        parent_rack = self._find_parent_rack(track, device)
        seq = Sequence()
        seq.add(ApplicationViewFacade.show_device)

        if not parent_rack:
            seq.add(partial(self._make_top_device_window_showable, track, device))
        else:
            seq.add(partial(self._make_nested_device_window_showable, track, device, parent_rack))

        return seq.done()

    def _make_top_device_window_showable(self, track, device):
        # type: (SimpleTrack, Device) -> Sequence
        devices_to_collapse = [d for d in track.devices if not d.is_collapsed]
        for d in devices_to_collapse:
            d.is_collapsed = True

        (x_device, y_device) = self._get_device_show_button_click_coordinates(track, device)

        seq = Sequence()
        seq.add(
            lambda: Backend.client().toggle_ableton_button(x=x_device, y=y_device, activate=True)
        )
        seq.wait(30)
        seq.add(partial(self._un_collapse_devices, devices_to_collapse))

        return seq.done()

    def _make_nested_device_window_showable(self, track, device, parent_rack):
        # type: (SimpleTrack, Device, RackDevice) -> Sequence
        devices_to_un_collapse = []  # type: List[Device]

        for d in track.devices:
            if d != parent_rack and not d.is_collapsed:
                devices_to_un_collapse.append(d)
                d.is_collapsed = True
        for d in parent_rack.chains[0].devices:
            if not d.is_collapsed:
                devices_to_un_collapse.append(d)
                d.is_collapsed = True

        (x_rack, y_rack) = self._get_rack_show_macros_button_click_coordinates(track, parent_rack)
        (x_device, y_device) = self._get_device_show_button_click_coordinates(
            track, device, parent_rack
        )

        seq = Sequence()
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_rack, y=y_rack, activate=False))
        seq.wait(5)
        seq.add(
            lambda: Backend.client().toggle_ableton_button(x=x_device, y=y_device, activate=True)
        )
        seq.wait(10)
        seq.add(lambda: Backend.client().toggle_ableton_button(x=x_rack, y=y_rack, activate=True))
        # at this point the rack macro controls could still be hidden if the plugin window masks the button
        seq.add(
            partial(self._un_collapse_devices, devices_to_un_collapse),
            name="restore device collapse state",
        )

        return seq.done()

    def _un_collapse_devices(self, devices_to_un_collapse):
        # type: (List[Device]) -> None
        for d in devices_to_un_collapse:
            d.is_collapsed = False

    def _get_device_show_button_click_coordinates(self, track, device, rack_device=None):
        # type: (SimpleTrack, Device, RackDevice) -> Tuple[int, int]
        """one grouping level only : expects all devices to be folded and macro controls hidden"""
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
            if len(rack_device.chains) >= 0:
                x += self.CHAIN_MIXER_PIXEL_WIDTH

        return (
            x - 3,
            y - 2,
        )  # we click not exactly in the center so as to know if the button is activated or not

    def _get_rack_show_macros_button_click_coordinates(self, track, rack_device):
        # type: (SimpleTrack, Device) -> Tuple[int, int]
        """top racks only : expects all devices to be folded"""
        parent_rack_position = list(track.devices).index(rack_device) + 1
        x = self._get_device_click_x_position(parent_rack_position)
        y = self.SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT

        return x, y

    def _get_device_click_x_position(self, device_position):
        # type: (int) -> int
        return self.WIDTH_PIXEL_OFFSET + device_position * self.COLLAPSED_DEVICE_PIXEL_WIDTH

    def _find_parent_rack(self, track, device):
        # type: (SimpleTrack, Device) -> Optional[RackDevice]
        if device in track.devices:
            return None

        for rack_device in [d for d in track.devices if isinstance(d, RackDevice)]:
            if device in rack_device.chains[0].devices:
                return rack_device

        raise Protocol0Error(
            "Couldn't find device %s (may be too nested to be detected)" % device.name
        )
