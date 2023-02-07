from typing import Optional, List, Type

import protocol0.domain.lom.instrument.instrument as instrument_package
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.utils import import_package


class InstrumentFactory(object):
    _INSTRUMENT_CLASSES = []  # type: List[Type[InstrumentInterface]]

    @classmethod
    def make_instrument_from_simple_track(cls, devices, instrument, track_name):
        # type: (SimpleTrackDevices, Optional[InstrumentInterface], str) -> Optional[InstrumentInterface]
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(lambda d: cls._get_instrument_class(d) is not None, devices)

        if instrument_device is None:
            instrument_device = find_if(
                lambda d: cls._get_instrument_class(d) is not None, devices.all
            )
        if instrument_device is None:
            return None

        instrument_class = cls._get_instrument_class(instrument_device)

        if (
            instrument_class
            and isinstance(instrument, instrument_class)
            and instrument.device == instrument_device
        ):
            return instrument  # maintaining state
        else:
            return instrument_class(instrument_device, track_name)

    @classmethod
    def _get_instrument_class(cls, device):
        # type: (Device) -> Optional[Type[InstrumentInterface]]
        # checking for grouped devices
        if isinstance(device, DrumRackDevice):
            from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import (
                InstrumentDrumRack,
            )

            return InstrumentDrumRack

        if isinstance(device, RackDevice):
            device = cls._get_device_from_instrument_rack_device(device) or device

        if isinstance(device, PluginDevice):
            for _class in cls._get_instrument_classes():
                if _class.DEVICE == device.enum:
                    return _class
        elif isinstance(device, SimplerDevice):
            from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import (
                InstrumentSimpler,
            )

            return InstrumentSimpler
        elif device._device.class_display_name == "Sampler":
            from protocol0.domain.lom.instrument.instrument.InstrumentSampler import (
                InstrumentSampler,
            )

            return InstrumentSampler

        return None

    @classmethod
    def _get_device_from_instrument_rack_device(cls, rack_device):
        # type: (RackDevice) -> Optional[Device]
        """Here, we fetch the appropriate instrument device from the instrument rack"""
        if len(rack_device.chains) and len(rack_device.chains[0].devices):
            # keeping only racks containing the same device
            device_types = list(
                set([type(chain.devices[0]) for chain in rack_device.chains if len(chain.devices)])
            )
            device_names = list(
                set([chain.devices[0].name for chain in rack_device.chains if len(chain.devices)])
            )
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
