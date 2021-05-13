from functools import partial

import Live
from typing import TYPE_CHECKING, Optional, Tuple, Dict, Type, cast

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import find_if

if TYPE_CHECKING:
    pass


class DeviceManager(AbstractControlSurfaceComponent):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 830
    SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT = 992
    COLLAPSED_DEVICE_PIXEL_WIDTH = 38
    COLLAPSED_RACK_DEVICE_PIXEL_WIDTH = 28
    WIDTH_PIXEL_OFFSET = 4

    def make_instrument_from_midi_track(self, track):
        # type: (SimpleMidiTrack) -> Optional[AbstractInstrument]
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(lambda d: AbstractInstrument.get_instrument_class(d), track.all_devices)  # type: ignore
        if not instrument_device:
            self.parent.log_error("Couldn't find instrument for midi track %s" % track)
            return None

        instrument_class = cast(Type[AbstractInstrument], AbstractInstrument.get_instrument_class(instrument_device))

        if isinstance(track.instrument, instrument_class):
            return track.instrument  # maintaining state
        else:
            return instrument_class(track=track, device=instrument_device)

    def update_rack(self, rack_device):
        # type: (Live.RackDevice.RackDevice) -> None
        """ update rack with the version stored in browser, keeping old values for identical parameters """
        parameters = {param.name: param.value for param in rack_device.parameters if "macro" not in param.name.lower()}
        self.song._view.select_device(rack_device)
        self.parent.browserManager.swap(rack_device.name)
        # restore values : this means we cannot dispatch values, only mappings
        # here 100ms is not enough
        self.parent._wait(1000, partial(self._update_device_params, rack_device, parameters))

    def _update_device_params(self, device, parameters):
        # type: (Device, Dict[str, float]) -> None
        for name, value in parameters.items():
            param = find_if(lambda p: p.name.lower() == name.lower(), device.parameters)
            if param and param.is_enabled:
                param.value = value

    def _get_device_click_x_position(self, device_position):
        # type: (int) -> int
        return self.WIDTH_PIXEL_OFFSET + device_position * self.COLLAPSED_DEVICE_PIXEL_WIDTH

    def make_plugin_window_showable(self, device):
        # type: (Device) -> Optional[Sequence]
        """ handles only one level of grouping in racks. Should be enough for now """
        if self.parent.keyboardShortcutManager.is_plugin_window_visible(device.name):
            return None
        self.parent.clyphxNavigationManager.show_track_view()

        seq = Sequence()
        parent_rack = self._find_parent_rack(device)

        if not parent_rack:
            for d in device.track.devices:
                d.is_collapsed = True
            (x_device, y_device) = self._get_device_show_button_click_coordinates(device)
            seq.add(
                lambda: self.parent.keyboardShortcutManager.send_click(x=x_device, y=y_device),
                name="click on device show button",
            )
            seq.add(wait=2)
            seq.add(lambda: setattr(device, "is_collapsed", False), name="uncollapse all devices")
        else:
            for d in device.track.devices:
                if d != parent_rack:
                    d.is_collapsed = True
            for d in parent_rack.chains[0].devices:
                d.is_collapsed = True

            (x_rack, y_rack) = self._get_rack_show_macros_button_click_coordinates(parent_rack)
            (x_device, y_device) = self._get_device_show_button_click_coordinates(device, parent_rack)

            seq.add(
                lambda: self.parent.keyboardShortcutManager.toggle_device_button(x=x_rack, y=y_rack, activate=False),
                wait=1,
                name="hide rack macro controls",
            )
            seq.add(
                lambda: self.parent.keyboardShortcutManager.send_click(x=x_device, y=y_device),
                wait=2,
                name="click on device show button",
            )
            seq.add(
                lambda: self.parent.keyboardShortcutManager.toggle_device_button(x=x_rack, y=y_rack, activate=True),
                wait=1,
                name="show rack macro controls",
            )

            def collapse_rack_devices():
                # type: () -> None
                for d in parent_rack.chains[0].devices:
                    d.is_collapsed = False

            seq.add(collapse_rack_devices)
            # at this point the rack macro controls could still be hidden if the plugin window masks the button

        seq.add(wait=3)

        return seq.done()

    def _get_device_show_button_click_coordinates(self, device, rack_device=None):
        # type: (Device, RackDevice) -> Tuple[int, int]
        """ one grouping level only : expects all devices to be folded and macro controls hidden """
        if not rack_device:
            device_position = device.track.devices.index(device) + 1
            x = self._get_device_click_x_position(device_position)
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT
        else:
            device_position = list(rack_device.chains[0].devices).index(device) + 1
            (x_rack, _) = self._get_rack_show_macros_button_click_coordinates(rack_device)
            x = x_rack + device_position * self.COLLAPSED_RACK_DEVICE_PIXEL_WIDTH
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT

        return (x, y)

    def _get_rack_show_macros_button_click_coordinates(self, rack_device):
        # type: (Device) -> Tuple[int, int]
        """ top racks only : expects all devices to be folded """
        parent_rack_position = rack_device.track.devices.index(rack_device) + 1
        x = self._get_device_click_x_position(parent_rack_position)
        y = self.SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT

        return (x, y)

    def _find_parent_rack(self, device):
        # type: (Device) -> Optional[RackDevice]
        if device in device.track.devices:
            return None

        for rack_device in [d for d in device.track.devices if isinstance(d, RackDevice)]:
            if device in rack_device.chains[0].devices:
                return rack_device

        raise Protocol0Error("Couldn't find device %s (may be too nested to be detected)" % device.name)
