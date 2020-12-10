import time
from functools import partial
from typing import TYPE_CHECKING, Optional

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class DeviceManager(AbstractControlSurfaceComponent):
    def scroll_current_track_selected_device_presets(self, track, go_next):
        # type: (AbstractTrack, bool) -> None
        device = self._get_device_to_scroll(track)
        if device is None:
            return
        if self._is_instrument(track, device):
            track.instrument.check_activated()
            track.instrument.action_scroll_presets_or_samples(go_next)
        elif not isinstance(device, Live.PluginDevice.PluginDevice):
            self.parent.browserManager.swap(None, ">" if go_next else "<")
        else:
            self.parent.log_debug("is plugin")
            self.parent.log_debug(list(device.presets))

    def _is_instrument(self, track, device):
        # type: (AbstractTrack, Live.Device.Device) -> bool
        # checks for simpler as device object is changing
        return track.instrument and device == track.instrument._device or isinstance(device,
                                                                                     Live.SimplerDevice.SimplerDevice)

    def _get_device_to_scroll(self, track):
        # type: (AbstractTrack) -> Optional[Live.Device.Device]
        # on selection of a the first rack either on simple or group track, we allow browsing the instrument as a shortcut
        if isinstance(track.selected_device, Live.RackDevice.RackDevice) and track.all_devices.index(
                track.selected_device) == 0 and track.instrument:
            return track.instrument._device
        elif isinstance(track.selected_device, Live.RackDevice.RackDevice):
            return None

        return track.selected_device

    def create_instrument_from_simple_track(self, track):
        # type: (SimpleTrack) -> AbstractInstrument
        from a_protocol_0.consts import INSTRUMENT_NAME_MAPPINGS
        from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler

        if not len(track.all_devices):
            return None

        simpler_device = find_if(lambda d: isinstance(d, Live.SimplerDevice.SimplerDevice), track.all_devices)
        if simpler_device:
            return InstrumentSimpler(track=track, device=simpler_device,
                                     has_rack=track.all_devices.index(simpler_device) != 0)

        plugin_device = find_if(lambda d: isinstance(d, Live.PluginDevice.PluginDevice), track.all_devices)
        if not plugin_device:
            return None

        if plugin_device.name not in INSTRUMENT_NAME_MAPPINGS:
            return None

        class_name = INSTRUMENT_NAME_MAPPINGS[plugin_device.name]
        try:
            mod = __import__('a_protocol_0.devices.' + class_name, fromlist=[class_name])
        except ImportError:
            self.parent.log_info("Import Error on instrument %s" % class_name)
            return None

        class_ = getattr(mod, class_name)
        return class_(track=track, device=plugin_device, has_rack=track.all_devices.index(plugin_device) != 0)

    def update_rack(self, rack_device):
        # type: (Live.RackDevice.RackDevice) -> None
        """ update rack with the version stored in browser, keeping old values for identical parameters """
        parameters = {param.name: param.value for param in rack_device.parameters if "macro" not in param.name.lower()}
        self.song.select_device(rack_device)
        self.parent.browserManager.swap(None, '"%s.adg"' % rack_device.name)
        # restore values : this means we cannot dispatch values, only mappings
        # here 100ms is not enough
        self.parent._wait(10, partial(self.update_device_params, rack_device, parameters))

    def update_device_params(self, device, parameters):
        for name, value in parameters.items():
            param = find_if(lambda p: p.name.lower() == name.lower(), device.parameters)
            if param and param.is_enabled:
                param.value = value
