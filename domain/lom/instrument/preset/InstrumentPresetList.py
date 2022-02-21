import os
from os.path import isfile, isdir

from typing import List, Optional, Any

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.shared.utils import find_if
from protocol0.shared.logging.Logger import Logger


class InstrumentPresetList(object):
    def __init__(self, device, preset_path, preset_extension, preset_display_option, track_name):
        # type: (Device, str, str, PresetDisplayOptionEnum, str) -> None
        self._device = device
        self._preset_path = preset_path
        self._preset_extension = preset_extension
        self._preset_display_option = preset_display_option
        self._track_name = track_name
        self._presets = None  # type: Optional[List[InstrumentPreset]]
        self._selected_preset = None  # type: Optional[InstrumentPreset]

    def __repr__(self, **k):
        # type: (Any) -> str
        return "preset count: %d, selected preset: %s" % (len(self.presets), self.selected_preset)

    @property
    def presets(self):
        # type: () -> List[InstrumentPreset]
        """ lazy loading """
        if self._presets is None:
            self.sync_presets()

        return self._presets  # type: ignore[return-value]

    @presets.setter
    def presets(self, presets):
        # type: (List[InstrumentPreset]) -> None
        self._presets = presets

    @property
    def selected_preset(self):
        # type: () -> Optional[InstrumentPreset]
        """ lazy loading """
        if self._presets is None:
            self.sync_presets()

        return self._selected_preset

    @selected_preset.setter
    def selected_preset(self, selected_preset):
        # type: (Optional[InstrumentPreset]) -> None
        """ lazy loading """
        self._selected_preset = selected_preset

    def sync_presets(self):
        # type: () -> None
        self.presets = self._import_presets()
        self.selected_preset = self._get_selected_preset()

    @property
    def categories(self):
        # type: () -> List[str]
        """ overridden """
        return sorted(list(set([preset.category for preset in self.presets if preset.category and not preset.category.startswith("_")])))

    @property
    def selected_category(self):
        # type: () -> str
        if self.selected_preset:
            return self.selected_preset.category
        else:
            return ""

    @selected_category.setter
    def selected_category(self, selected_category):
        # type: (Optional[str]) -> None
        self.selected_preset = self._category_presets(selected_category)[0]

    def _category_presets(self, category=None):
        # type: (Optional[str]) -> List[InstrumentPreset]
        return list(filter(lambda p: p.category == (category or self.selected_category), self.presets))

    def scroll(self, go_next):
        # type: (bool) -> None
        if isinstance(self._device, RackDevice):
            self._device.scroll_chain_selector(go_next=go_next)
            self.selected_preset = self.presets[int(self._device.chain_selector.value)]
            return

        category_presets = self._category_presets()
        if len(category_presets) == 0:
            Logger.log_warning(
                "Didn't find category presets for cat %s in %s" % (self.selected_category, self._device)
            )
            if len(self.categories) == 0:
                Logger.log_error("Didn't find categories for %s" % self)
                return

            self.selected_category = self.categories[0]
            return self.scroll(go_next=go_next)

        if self.selected_preset and self.selected_category and self.selected_preset.category != self.selected_category:
            new_preset_index = 0
        else:
            offset = category_presets[0].index
            selected_preset_index = self.selected_preset.index if self.selected_preset else 0
            new_preset_index = selected_preset_index + (1 if go_next else -1) - offset

        self.selected_preset = category_presets[new_preset_index % len(category_presets)]

    def _import_presets(self):
        # type: () -> List[InstrumentPreset]
        if not self._preset_path:
            # Addictive keys or any other multi instrument rack
            if isinstance(self._device, RackDevice):
                return [
                    InstrumentPreset(index=i, name=chain.name)
                    for i, chain in enumerate(self._device.chains)
                ]
            # Prophet rev2 other vst with accessible presets list
            elif isinstance(self._device, PluginDevice) and len(self._device.presets):
                return [
                    InstrumentPreset(index=i, name=preset)
                    for i, preset in enumerate(self._device.presets[0:128])
                ]
        # Serum or any other vst storing presets in a text file
        elif isfile(self._preset_path):
            return [
                InstrumentPreset(index=i, name=name)
                for i, name in enumerate(open(self._preset_path).readlines()[0:128])
            ]
        # Simpler or Minitaur or any instrument storing presets as files in a directory
        elif isdir(self._preset_path):
            presets = []
            has_categories = False
            for root, dir_names, files in os.walk(self._preset_path):
                if len(dir_names):
                    has_categories = True
                if has_categories:
                    if root == self._preset_path:
                        continue

                    category = root.replace(self._preset_path + "\\", "").split("\\")[0]
                    for filename in [filename for filename in files if
                                     filename.endswith(self._preset_extension)]:
                        presets.append(
                            InstrumentPreset(index=len(presets), category=category, name=filename))
                else:
                    for filename in [filename for filename in files if
                                     filename.endswith(self._preset_extension)]:
                        presets.append(InstrumentPreset(index=len(presets), name=filename))

            return presets

        Logger.log_error("Couldn't import presets for %s" % self._device)
        return []

    def _get_selected_preset(self):
        # type: () -> Optional[InstrumentPreset]
        """
        Checking first the track name (Serum or Minitaur)
        then the device name (e.g. simpler)
        """
        preset = None

        if len(self.presets) == 0:
            return None

        if self._device and self._device.preset_name:
            preset = find_if(lambda p: p.name == self._device.preset_name, self.presets)
        elif self._preset_display_option == PresetDisplayOptionEnum.NAME:
            preset = find_if(lambda p: p.name == self._track_name, self.presets)

        return preset
