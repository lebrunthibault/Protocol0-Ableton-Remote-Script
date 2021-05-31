import os
from os.path import isfile, isdir

from typing import TYPE_CHECKING, List, Optional, Any

from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.utils.utils import find_if

if TYPE_CHECKING:
    from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentPresetList(AbstractObject):
    def __init__(self, instrument, *a, **k):
        # type: (AbstractInstrument, Any, Any) -> None
        super(InstrumentPresetList, self).__init__(*a, **k)
        self.instrument = instrument
        self.presets = []  # type: List[InstrumentPreset]
        self.selected_preset = None  # type: Optional[InstrumentPreset]

    def __repr__(self):
        # type: () -> str
        return "preset count: %d, selected preset: %s" % (len(self.presets), self.selected_preset)

    def sync_presets(self):
        # type: () -> None
        self.presets = self._import_presets()
        self.selected_preset = self._get_selected_preset()
        # noinspection PyUnresolvedReferences
        self.instrument.notify_selected_preset()

    @property
    def categories(self):
        # type: () -> List[str]
        """ overridden """
        return list(set([preset.category for preset in self.presets if preset.category]))

    @property
    def selected_category(self):
        # type: () -> Optional[str]
        if self.selected_preset:
            return self.selected_preset.category
        elif len(self.categories):
            return self.categories[0]
        else:
            return None

    @selected_category.setter
    def selected_category(self, selected_category):
        # type: (Optional[str]) -> None
        self.selected_preset = self.category_presets(selected_category)[0]

    def category_presets(self, category=None):
        # type: (Optional[str]) -> List[InstrumentPreset]
        return list(filter(lambda p: p.category == (category or self.selected_category), self.presets))

    def scroll(self, go_next):
        # type: (bool) -> None
        category_presets = self.category_presets()
        if len(category_presets) == 0:
            self.parent.log_warning(
                "Didn't find category presets for cat %s in %s" % (self.selected_category, self.instrument)
            )
            return
        if self.selected_category and self.selected_preset.category != self.selected_category:
            new_preset_index = 0
        else:
            offset = category_presets[0].index
            new_preset_index = self.selected_preset.index + (1 if go_next else -1) - offset

        self.selected_preset = category_presets[new_preset_index % len(category_presets)]
        if isinstance(self.instrument.device, RackDevice):
            self.instrument.device.scroll_chain_selector(go_next=go_next)

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        if not self.instrument.presets_path:
            return [self.instrument.make_preset(index=i) for i in range(0, self.instrument.DEFAULT_NUMBER_OF_PRESETS)]
        elif isfile(self.instrument.presets_path):
            return [
                self.instrument.make_preset(index=i, name=name)
                for i, name in enumerate(open(self.instrument.presets_path).readlines())
            ]
        elif isdir(self.instrument.presets_path):
            presets = []
            for root, dir_names, files in os.walk(self.instrument.presets_path):
                has_categories = len(dir_names)
                if has_categories:
                    if root == self.instrument.presets_path:
                        continue

                    category = root.replace(self.instrument.presets_path + "\\", "").split("\\")[0]
                    for file in [file for file in files if file.endswith(self.instrument.PRESET_EXTENSION)]:
                        presets.append(self.instrument.make_preset(index=len(presets), category=category, name=file))
                else:
                    for file in [file for file in files if file.endswith(self.instrument.PRESET_EXTENSION)]:
                        presets.append(self.instrument.make_preset(index=len(presets), name=file))

            return presets

        self.parent.log_error("Couldn't import presets for %s" % self.instrument)
        return []

    def _get_selected_preset(self):
        # type: () -> Optional[InstrumentPreset]
        """
        Checking first the track name (Serum or Minitaur)
        then the device name (e.g. simpler)
        then the track selected index (prophet, fallback)
        """
        preset = None

        if self.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME:
            preset = find_if(lambda preset: preset.name == self.instrument.track.abstract_track.name, self.presets)
        else:
            preset = find_if(lambda preset: preset.name == self.instrument.preset_name, self.presets)

        try:
            return preset or self.presets[self.instrument.track.abstract_track.track_name.selected_preset_index]
        except IndexError:
            if len(self.presets):
                return self.presets[0]
            else:
                return None
