from functools import partial

from typing import Optional, Tuple, Dict, Type, cast, List

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.Device import Device
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if


class DeviceManager(AbstractControlSurfaceComponent):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 830
    SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT = 992
    COLLAPSED_DEVICE_PIXEL_WIDTH = 38
    COLLAPSED_RACK_DEVICE_PIXEL_WIDTH = 28
    WIDTH_PIXEL_OFFSET = 4

    def make_instrument_from_simple_track(self, track):
        # type: (SimpleTrack) -> Optional[AbstractInstrument]
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(lambda d: AbstractInstrument.get_instrument_class(d),  # type: ignore
                                    track.all_devices)
        if not instrument_device:
            # self.parent.log_warning("Couldn't find instrument for track %s" % track)
            return None

        instrument_class = cast(Type[AbstractInstrument], AbstractInstrument.get_instrument_class(instrument_device))

        if isinstance(track.instrument, instrument_class):
            return track.instrument  # maintaining state
        else:
            return instrument_class(track=track, device=instrument_device)

    def update_audio_effect_rack(self, device):
        # type: (RackDevice) -> Sequence
        """ update rack with the version stored in browser, keeping old values for identical parameters """
        self.parent.log_info("selecting and updating device %s (track %s)" % (device, device.track))
        parameters = {param.name: param.value for param in device.parameters if "macro" not in param.name.lower()}
        device_name = device.name
        seq = Sequence()
        seq.add(partial(self.song.select_device, device))
        seq.add(partial(self.parent.browserManager.update_audio_effect_preset, device))
        seq.add(partial(self._update_device_params, device.track, device.name, parameters))
        return seq.done()

    def _update_device_params(self, track, device_name, parameters):
        # type: (SimpleTrack, str, Dict[str, float]) -> None
        device = find_if(lambda d: d.name == device_name, track.devices)
        for name, value in parameters.items():
            param = find_if(lambda p: p.name.lower() == name.lower(), device.parameters)
            if param and param.is_enabled:
                param.value = value

    def _get_device_click_x_position(self, device_position):
        # type: (int) -> int
        return self.WIDTH_PIXEL_OFFSET + device_position * self.COLLAPSED_DEVICE_PIXEL_WIDTH

    def make_plugin_window_showable(self, device):
        # type: (Device) -> Sequence
        """ handles only one level of grouping in racks. Should be enough for now """
        parent_rack = self._find_parent_rack(device)
        seq = Sequence()
        seq.add(self.parent.navigationManager.show_device_view)

        if not parent_rack:
            seq.add(partial(self._make_top_device_window_showable, device))
        else:
            seq.add(partial(self._make_nested_device_window_showable, device, parent_rack))

        seq.add(self.system.show_plugins)

        return seq.done()

    def _make_top_device_window_showable(self, device):
        # type: (Device) -> Sequence
        devices_to_uncollapse = []  # type: List[Device]

        for d in device.track.devices:
            if not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True
        (x_device, y_device) = self._get_device_show_button_click_coordinates(device)
        seq = Sequence()
        seq.add(
            lambda: self.system.click(x=x_device, y=y_device),
            wait=2,
            name="click on device show button",
        )
        seq.add(partial(self.uncollapse_devices, devices_to_uncollapse), name="restore device collapse state")

        return seq.done()

    def _make_nested_device_window_showable(self, device, parent_rack):
        # type: (Device, RackDevice) -> Sequence
        devices_to_uncollapse = []  # type: List[Device]

        for d in device.track.devices:
            if d != parent_rack and not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True
        for d in parent_rack.chains[0].devices:
            if not d.is_collapsed:
                devices_to_uncollapse.append(d)
                d.is_collapsed = True

        (x_rack, y_rack) = self._get_rack_show_macros_button_click_coordinates(parent_rack)
        (x_device, y_device) = self._get_device_show_button_click_coordinates(device, parent_rack)

        seq = Sequence()
        seq.add(
            lambda: self.system.toggle_ableton_button(x=x_rack, y=y_rack, activate=False),
            wait=3,
            name="hide rack macro controls",
        )
        seq.add(
            lambda: self.system.click(x=x_device, y=y_device),
            wait=5,
            name="click on device show button",
        )
        seq.add(
            lambda: self.system.toggle_ableton_button(x=x_rack, y=y_rack, activate=True),
            name="show rack macro controls",
        )
        # at this point the rack macro controls could still be hidden if the plugin window masks the button
        seq.add(partial(self.uncollapse_devices, devices_to_uncollapse), name="restore device collapse state")

        return seq.done()

    def uncollapse_devices(self, devices_to_uncollapse):
        # type: (List[Device]) -> None
        for d in devices_to_uncollapse:
            d.is_collapsed = False

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
