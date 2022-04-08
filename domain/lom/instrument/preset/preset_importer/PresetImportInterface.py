from typing import List, Dict

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetImportInterface(object):
    PRESET_CACHE = {}  # type: Dict[str, List[InstrumentPreset]]

    def import_presets(self):
        # type: () -> List[InstrumentPreset]
        cache_key = getattr(self, "_path", None)
        if cache_key is not None and cache_key in self.PRESET_CACHE:
            return self.PRESET_CACHE[cache_key]
        else:
            presets = self._import_presets()
            if cache_key is not None:
                self.PRESET_CACHE[cache_key] = presets
            return presets

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        raise NotImplementedError
