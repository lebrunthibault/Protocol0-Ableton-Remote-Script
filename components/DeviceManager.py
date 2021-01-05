from functools import partial
from typing import TYPE_CHECKING, Optional, List, Tuple

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import EXTERNAL_SYNTH_MINITAUR_NAME
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class DeviceManager(AbstractControlSurfaceComponent):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 830
    SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT = 992
    COLLAPSED_DEVICE_PIXEL_WIDTH = 38
    COLLAPSED_RACK_DEVICE_PIXEL_WIDTH = 28
    WIDTH_PIXEL_OFFSET = 4

    def is_track_instrument(self, track, device):
        # type: (AbstractTrack, Live.Device.Device) -> bool
        # checks for simpler as device object is changing
        return (track.instrument and device == track.instrument._device) or isinstance(device,
                                                                                       Live.SimplerDevice.SimplerDevice)

    def create_instrument_from_simple_track(self, track):
        # type: (SimpleTrack) -> AbstractInstrument
        from a_protocol_0.consts import INSTRUMENT_NAME_MAPPINGS
        from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler
        from a_protocol_0.devices.InstrumentMinitaur import InstrumentMinitaur

        if not len(track.all_devices):
            return None

        simpler_device = find_if(lambda d: isinstance(d, Live.SimplerDevice.SimplerDevice), track.all_devices)
        if simpler_device:
            return InstrumentSimpler(track=track, device=simpler_device)

        instrument_device = find_if(
            lambda d: isinstance(d, Live.PluginDevice.PluginDevice) and d.name in INSTRUMENT_NAME_MAPPINGS,
            track.all_devices)
        if not instrument_device:
            if EXTERNAL_SYNTH_MINITAUR_NAME in track.name:
                return InstrumentMinitaur(track=track, device=None)
            else:
                return None

        class_name = INSTRUMENT_NAME_MAPPINGS[instrument_device.name]
        try:
            mod = __import__('a_protocol_0.devices.' + class_name, fromlist=[class_name])
        except ImportError:
            self.parent.log_info("Import Error on instrument %s" % class_name)
            return None

        class_ = getattr(mod, class_name)
        return class_(track=track, device=instrument_device)

    def update_rack(self, rack_device):
        # type: (Live.RackDevice.RackDevice) -> None
        """ update rack with the version stored in browser, keeping old values for identical parameters """
        parameters = {param.name: param.value for param in rack_device.parameters if "macro" not in param.name.lower()}
        self.song.select_device(rack_device)
        self.parent.browserManager.swap(rack_device.name)
        # restore values : this means we cannot dispatch values, only mappings
        # here 100ms is not enough
        self.parent._wait(10, partial(self._update_device_params, rack_device, parameters))

    def _update_device_params(self, device, parameters):
        for name, value in parameters.items():
            param = find_if(lambda p: p.name.lower() == name.lower(), device.parameters)
            if param and param.is_enabled:
                param.value = value

    def _scroll_current_track_selected_device_presets(self, track, go_next):
        # type: (AbstractTrack, bool) -> None
        """ deprecated for now """
        device = self._get_device_to_scroll(track)
        if device is None:
            return
        if self.is_track_instrument(track, device):
            track.instrument.action_scroll_presets_or_samples(go_next)
        elif not isinstance(device, Live.PluginDevice.PluginDevice):
            self.parent.browserManager.swap(">" if go_next else "<")
        elif isinstance(device, Live.PluginDevice.PluginDevice):
            self.parent.log_info("is plugin")
            # self.parent.log_info(list(device.presets))

    def _get_device_to_scroll(self, track):
        # type: (AbstractTrack) -> Optional[Live.Device.Device]
        """ deprecated for now """
        # on selection of a the first rack either on simple or group track, we allow browsing the instrument as a shortcut
        if isinstance(track.selected_device, Live.RackDevice.RackDevice) and track.all_devices.index(
                track.selected_device) == 0 and track.instrument:
            return track.instrument._device
        elif isinstance(track.selected_device, Live.RackDevice.RackDevice):
            return None

        return track.selected_device

    def _get_device_click_x_position(self, device_position):
        return self.WIDTH_PIXEL_OFFSET + device_position * self.COLLAPSED_DEVICE_PIXEL_WIDTH

    def is_plugin_window_visible(self, device=None, try_show=False, sync=False):
        # type: (Live.Device.Device, bool, bool) -> Sequence
        seq = Sequence(auto_start=sync)
        if try_show:
            seq.add(self.parent.keyboardShortcutManager.show_plugins, do_if_not=self.parent.keyboardShortcutManager.is_plugin_window_visible, wait=1)

        seq.add(self.parent.keyboardShortcutManager.is_plugin_window_visible)

        return seq.done()

    def check_plugin_window_showable(self, device, track):
        # type: (Live.Device.Device, SimpleTrack) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(self._make_device_showable, device, track), do_if_not=partial(self.is_plugin_window_visible, device, try_show=True))
        return seq.done()

    def _make_device_showable(self, device, track):
        # type: (Live.Device.Device, SimpleTrack) -> Sequence
        """ handles only one level of grouping in racks. Should be enough for now """
        seq = Sequence()
        parent_rack = self._find_device_parent(device, track.devices)

        if not parent_rack:
            [setattr(d.view, "is_collapsed", True) for d in track.devices]
            (x_device, y_device) = self._get_device_show_button_click_coordinates(track, device)
            seq.add(lambda: self.parent.keyboardShortcutManager.send_click(x=x_device, y=y_device), wait=1, name="click on device show button")
            seq.add(lambda: setattr(device.view, "is_collapsed", False), wait=1, name="uncollapse all devices")
        else:
            [setattr(d.view, "is_collapsed", True) for d in track.devices if d != parent_rack]
            [setattr(d.view, "is_collapsed", True) for d in parent_rack.chains[0].devices]

            (x_rack, y_rack) = self._get_rack_show_macros_button_click_coordinates(track, parent_rack)
            (x_device, y_device) = self._get_device_show_button_click_coordinates(track, device, parent_rack)

            seq.add(lambda: self.parent.keyboardShortcutManager.toggle_device_button(x=x_rack, y=y_rack, activate=False), wait=1, name="hide rack macro controls")
            seq.add(lambda: self.parent.keyboardShortcutManager.send_click(x=x_device, y=y_device), wait=1, name="click on device show button")
            seq.add(lambda: self.parent.keyboardShortcutManager.toggle_device_button(x=x_rack, y=y_rack, activate=True), wait=1, name="show rack macro controls")
            seq.add(lambda: [setattr(d.view, "is_collapsed", False) for d in parent_rack.chains[0].devices], wait=0, name="uncollapse all rack devices")
            # at this point the rack macro controls could still be hidden if the plugin window masks the button

        return seq.done()

    def _get_device_show_button_click_coordinates(self, track, device, rack_device=None):
        # type: (SimpleTrack, Live.Device.Device, Live.RackDevice.RackDevice) -> Tuple[int]
        """ one grouping level only : expects all devices to be folded and macro controls hidden """
        if not rack_device:
            device_position = track.devices.index(device) + 1
            x = self._get_device_click_x_position(device_position)
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT
        else:
            device_position = list(rack_device.chains[0].devices).index(device) + 1
            (x_rack, _) = self._get_rack_show_macros_button_click_coordinates(track, rack_device)
            x = x_rack + device_position * self.COLLAPSED_RACK_DEVICE_PIXEL_WIDTH
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT

        return (x, y)

    def _get_rack_show_macros_button_click_coordinates(self, track, rack_device):
        # type: (SimpleTrack, Live.RackDevice.RackDevice) -> Tuple[int]
        """ top racks only : expects all devices to be folded """
        parent_rack_position = track.devices.index(rack_device) + 1
        x = self._get_device_click_x_position(parent_rack_position)
        y = self.SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT

        return (x, y)

    def _find_device_parent(self, device, devices):
        # type: (Live.Device.Device, List[Live.Device.Device]) -> Live.RackDevice.RackDevice
        if device in devices:
            return None

        for rack_device in devices:
            if isinstance(rack_device, Live.RackDevice.RackDevice) and device in rack_device.chains[0].devices:
                return rack_device

        return None
