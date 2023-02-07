from os.path import isfile, isdir

from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import (
    DirectoryPresetImporter,
)
from protocol0.domain.lom.instrument.preset.preset_importer.FilePresetImporter import (
    FilePresetImporter,
)
from protocol0.domain.lom.instrument.preset.preset_importer.NullPresetImporter import \
    NullPresetImporter
from protocol0.domain.lom.instrument.preset.preset_importer.PluginDevicePresetImporter import (
    PluginDevicePresetImporter,
)
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)
from protocol0.domain.lom.instrument.preset.preset_importer.RackDevicePresetImporter import (
    RackDevicePresetImporter,
)
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class PresetImporterFactory(object):
    @classmethod
    def create_importer(cls, device, preset_path, preset_extension):
        # type: (Optional[Device], str, str) -> PresetImportInterface
        if not preset_path or not preset_extension:
            return NullPresetImporter()
        elif isinstance(device, RackDevice):
            return RackDevicePresetImporter(device)
        elif isinstance(device, PluginDevice):
            return PluginDevicePresetImporter(device)
        elif isfile(preset_path):
            return FilePresetImporter(preset_path)
        elif isdir(preset_path):
            return DirectoryPresetImporter(preset_path, preset_extension)
        else:
            raise Protocol0Error("Couldn't import presets for %s" % device)
