from functools import partial
from typing import TYPE_CHECKING, Optional, List

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import EXTERNAL_SYNTH_MINITAUR_NAME
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class DeviceManager(AbstractControlSurfaceComponent):
    SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT = 824
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

    def show_device(self, device, track):
        # type: (Live.Device.Device, SimpleTrack) -> None
        parent_rack = self._find_device_parent(device, track.top_devices)
        if not parent_rack:
            [setattr(d.view, "is_collapsed", True) for d in track.top_devices]
            device_position = track.top_devices.index(device) + 1
            x = self._get_device_click_x_position(device_position)
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT
            self.parent.keyboardShortcutManager.sendClick(x=x, y=y)
            self.parent.defer(lambda: setattr(device.view, "is_collapsed", False))
        else:
            [setattr(d.view, "is_collapsed", True) for d in track.top_devices if d != parent_rack]
            parent_rack_position = track.top_devices.index(parent_rack) + 1
            x_rack = self._get_device_click_x_position(parent_rack_position)
            y_rack = self.SHOW_HIDE_MACRO_BUTTON_PIXEL_HEIGHT
            self.parent.keyboardShortcutManager.sendClick(x=x_rack, y=y_rack)
            [setattr(d.view, "is_collapsed", True) for d in parent_rack.chains[0].devices]
            device_position = list(parent_rack.chains[0].devices).index(device) + 1
            x = x_rack + device_position * self.COLLAPSED_RACK_DEVICE_PIXEL_WIDTH
            y = self.SHOW_HIDE_PLUGIN_BUTTON_PIXEL_HEIGHT
            self.parent.keyboardShortcutManager.sendClick(x=x, y=y)
            self.parent.defer(lambda: self.parent.keyboardShortcutManager.sendClick(x=x_rack, y=y_rack))
            self.parent.defer(lambda: [setattr(d.view, "is_collapsed", False) for d in parent_rack.chains[0].devices])

    def _find_device_parent(self, device, devices):
        # type: (Live.Device.Device, List[Live.Device.Device]) -> Live.RackDevice.RackDevice
        if device in devices:
            return None

        for rack_device in devices:
            if isinstance(rack_device, Live.RackDevice.RackDevice) and device in rack_device.chains[0].devices:
                return rack_device

        return None

