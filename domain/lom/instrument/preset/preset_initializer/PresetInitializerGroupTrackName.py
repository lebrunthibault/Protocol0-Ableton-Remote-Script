from typing import List, Optional

from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import \
    PresetInitializerInterface
from protocol0.domain.shared.utils import find_if


class PresetInitializerGroupTrackName(PresetInitializerInterface):
    def get_selected_preset(self, presets):
        # type: (List[InstrumentPreset]) -> Optional[InstrumentPreset]
        assert self._track.group_track
        return find_if(lambda p: p.name == self._track.group_track.name, presets)
