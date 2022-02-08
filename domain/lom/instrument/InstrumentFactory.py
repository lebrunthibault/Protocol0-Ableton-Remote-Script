from typing import Optional, List, Type, TYPE_CHECKING

import protocol0.domain.lom.instrument.instrument as instrument_package
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.shared.utils import find_if, import_package
from protocol0.shared.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentFactory(object):
    _INSTRUMENT_CLASSES = []  # type: List[Type[InstrumentInterface]]

    @classmethod
    def make_instrument_from_simple_track(cls, track):
        # type: (SimpleTrack) -> Optional[InstrumentInterface]
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(lambda d: cls._get_instrument_class(d) is not None, track.all_devices)
        Logger.log_dev("instrument_device: %s" % instrument_device)
        if not instrument_device:
            return None

        instrument_class = cls._get_instrument_class(instrument_device)

        if isinstance(track.instrument, instrument_class):
            return track.instrument  # maintaining state
        else:
            return instrument_class(track=track, device=instrument_device)

    @classmethod
    def _get_instrument_class(cls, device):
        # type: (Device) -> Optional[Type[InstrumentInterface]]
        # checking for grouped devices
        if isinstance(device, RackDevice):
            device = cls._get_device_from_rack_device(device) or device

        if isinstance(device, PluginDevice):
            Logger.log_dev("cls._get_instrument_classes: %s" % cls._get_instrument_classes())
            for _class in cls._get_instrument_classes():
                if _class.DEVICE_NAME.lower() == device.name.lower():
                    return _class
        elif isinstance(device, SimplerDevice):
            from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import InstrumentSimpler

            return InstrumentSimpler
        elif device.can_have_drum_pads:
            from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack

            return InstrumentDrumRack

        return None

    @classmethod
    def _get_device_from_rack_device(cls, rack_device):
        # type: (RackDevice) -> Optional[Device]
        if len(rack_device.chains) and len(rack_device.chains[0].devices):
            # keeping only racks containing the same device
            device_types = list(set([type(chain.devices[0]) for chain in rack_device.chains if len(chain.devices)]))
            device_names = list(set([chain.devices[0].name for chain in rack_device.chains if len(chain.devices)]))
            if len(device_types) == 1 and len(device_names) == 1:
                return rack_device.chains[0].devices[0]

        return None

    @classmethod
    def _get_instrument_classes(cls):
        # type: () -> List[Type[InstrumentInterface]]
        if not cls._INSTRUMENT_CLASSES:
            import_package(instrument_package)
            cls._INSTRUMENT_CLASSES = InstrumentInterface.__subclasses__()

        return cls._INSTRUMENT_CLASSES
