from functools import partial

from typing import TYPE_CHECKING, Optional, List

from a_protocol_0.devices.presets.InstrumentPreset import InstrumentPreset
from a_protocol_0.devices.presets.InstrumentPresetList import InstrumentPresetList
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import scroll_values

if TYPE_CHECKING:
    from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class AbstractInstrumentPresetsMixin(object):
    DEFAULT_NUMBER_OF_PRESETS = 128
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = False
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    PROGRAM_CHANGE_OFFSET = 0  # if we store presets not at the beginning of the list

    def _import_presets(self):
        # type: (AbstractInstrument) -> None
        self._preset_list = InstrumentPresetList(self)  # type: InstrumentPresetList
        self._preset_list.sync_presets()

    @property
    def selected_preset(self):
        # type: (AbstractInstrument) -> Optional[InstrumentPreset]
        return self._preset_list.selected_preset

    @property
    def should_display_selected_preset_name(self):
        # type: (AbstractInstrument) -> bool
        return self._preset_list.has_preset_names and self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME

    @property
    def presets_path(self):
        # type: (AbstractInstrument) -> str
        """ overridden """
        return self.PRESETS_PATH

    def format_preset_name(self, preset_name):
        # type: (AbstractInstrument, str) -> str
        """ overridden """
        return preset_name

    @property
    def preset_name(self):
        # type: (AbstractInstrument) -> str
        """ overridden """
        return self.name

    def scroll_presets_or_samples(self, go_next):
        # type: (AbstractInstrument, bool) -> Sequence
        self.parent.navigationManager.show_device_view()

        seq = Sequence()
        if self.NEEDS_ACTIVATION_FOR_PRESETS_CHANGE:
            seq.add(self.check_activated)

        seq.add(partial(self._preset_list.scroll, go_next=go_next))
        seq.add(partial(self._sync_selected_preset))
        return seq.done()

    @property
    def categories(self):
        # type: (AbstractInstrument) -> (List[str])
        """ overridden """
        return []

    @property
    def selected_category(self):
        # type: (AbstractInstrument) -> Optional[str]
        return self._selected_category

    @selected_category.setter
    def selected_category(self, selected_category):
        # type: (AbstractInstrument, Optional[str]) -> None
        self._selected_category = selected_category
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            self.track.track_name.update(base_name=selected_category)

    def scroll_preset_categories(self, go_next):
        # type: (AbstractInstrument, bool) -> None
        if not len(self.categories):
            self.parent.show_message("this instrument does not have categories")
            return
        if not self.selected_category:
            self.parent.log_error("Couldn't find the selected category")
            return
        self.parent.navigationManager.show_device_view()
        self.parent.log_dev("self.categories: %s" % self.categories)
        self.parent.log_dev("self.selected_category: %s" % self.selected_category)

        self.selected_category = scroll_values(self.categories, self.selected_category, go_next)
        self.parent.log_dev("self.selected_category: %s" % self.selected_category)

    def _sync_selected_preset(self):
        # type: (AbstractInstrument) -> Sequence
        seq = Sequence()
        self.parent.log_dev(" self.selected_preset: %s" % self.selected_preset)
        seq.add(partial(self._load_preset, self.selected_preset))
        seq.add(partial(self.parent.show_message, "preset change : %s" % self.selected_preset))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_selected_preset)
        return seq.done()

    def _load_preset(self, preset):
        # type: (AbstractInstrument, InstrumentPreset) -> Optional[Sequence]
        """ Overridden default is send program change """
        seq = Sequence()
        seq.add(self.track.abstract_track.arm)
        if not isinstance(self.device, RackDevice):
            seq.add(partial(self.parent.midiManager.send_program_change, preset.index + self.PROGRAM_CHANGE_OFFSET))
        return seq.done()
