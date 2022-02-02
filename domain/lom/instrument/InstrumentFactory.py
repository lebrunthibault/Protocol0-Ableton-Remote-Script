import os
import re
from os import listdir

from typing import Optional, List, Type

from protocol0.domain.errors.Protocol0Error import Protocol0Error
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.AbstractInstrument import AbstractInstrument
from protocol0.infra.log import log_ableton


class InstrumentFactory(object):
    INSTRUMENT_CLASSES = {}

    @classmethod
    def get_instrument_class(cls, device):
        # type: (Device) -> Optional[Type[AbstractInstrument]]
        # checking for grouped devices
        if isinstance(device, RackDevice):
            device = cls._get_device_from_rack_device(device) or device

        if isinstance(device, PluginDevice):
            for _class in cls.get_instrument_classes():
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
    def get_instrument_classes(cls):
        # type: () -> List[Type[AbstractInstrument]]
        if not cls.INSTRUMENT_CLASSES:
            cls.INSTRUMENT_CLASSES = cls._get_instrument_classes()

        return cls.INSTRUMENT_CLASSES

    @classmethod
    def _get_instrument_classes(cls):
        # type: () -> List[Type[AbstractInstrument]]
        files = listdir(os.path.dirname(os.path.abspath(__file__)) + "/instrument")
        log_ableton(os.path.dirname(os.path.abspath(__file__)) + "/instrument")
        log_ableton(files)

        class_names = []
        for instrument_file in [instrument_file for instrument_file in files
                                if re.match("^Instrument[a-zA-Z]*\\.py$", instrument_file)]:
            class_name = instrument_file.replace(".py", "")
            try:
                mod = __import__("protocol0.domain.lom.instrument.instrument." + class_name, fromlist=[class_name])
            except ImportError:
                raise Protocol0Error("Import Error on class %s" % class_name)

            class_names.append(getattr(mod, class_name))

        return class_names
