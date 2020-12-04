from typing import TYPE_CHECKING

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_pushbase.device_chain_utils import is_simpler

from a_protocol_0.utils.utils import find_all_devices

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class InstrumentManager(AbstractControlSurfaceComponent):
    def create_from_simple_track(self, track):
        # type: (SimpleTrack) -> AbstractInstrument
        from a_protocol_0.consts import INSTRUMENT_NAME_MAPPINGS
        from a_protocol_0.devices.InstrumentSimpler import InstrumentSimpler

        devices = list(find_all_devices(track._track))
        if not len(devices):
            return None

        instrument_device = find_if(lambda d: isinstance(d, Live.PluginDevice.PluginDevice), devices)
        if not instrument_device:
            return None

        has_rack = devices.index(instrument_device) != 0
        if is_simpler(instrument_device):
            return InstrumentSimpler(track=track, device=instrument_device, has_rack=has_rack)

        if instrument_device.name not in INSTRUMENT_NAME_MAPPINGS:
            # self.parent.log(
            #     "Couldn't match instrument with name to an instrument class %s" % instrument_device.name)
            return None

        class_name = INSTRUMENT_NAME_MAPPINGS[instrument_device.name]
        try:
            mod = __import__('a_protocol_0.devices.' + class_name, fromlist=[class_name])
        except ImportError:
            self.parent.log("Import Error on instrument %s" % class_name)
            return None

        class_ = getattr(mod, class_name)
        return class_(track=track, device=instrument_device, has_rack=has_rack)
