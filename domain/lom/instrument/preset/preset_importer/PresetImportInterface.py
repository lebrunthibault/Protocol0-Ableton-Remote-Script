from typing import List, Type, Dict

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetImportInterface(object):
    PRESET_CACHE = {}  # type: Dict[Type, List[InstrumentPreset]]

    def import_presets(self):
        # type: () -> List[InstrumentPreset]
        cache_key = self.__class__
        if cache_key in self.PRESET_CACHE:
            return self.PRESET_CACHE[cache_key]
        else:
            presets = self._import_presets()
            self.PRESET_CACHE[cache_key] = presets
            return presets

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        raise NotImplementedError
