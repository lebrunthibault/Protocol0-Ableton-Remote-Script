from functools import partial

from typing import TYPE_CHECKING, Optional

from _Framework.Util import forward_property
from protocol0.devices.presets.InstrumentPreset import InstrumentPreset
from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.lom.device.PluginDevice import PluginDevice
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.devices.AbstractInstrument import AbstractInstrument


class AbstractInstrumentPresetsMixin(object):
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    PROGRAM_CHANGE_OFFSET = 0  # if we store presets not at the beginning of the list

    def make_preset(self, index, name=None, category=None):
        # type: (AbstractInstrument, int, Optional[basestring], Optional[str]) -> InstrumentPreset
        """ overridden """
        return InstrumentPreset(instrument=self, index=index, name=name, category=category)

    # noinspection PyMethodParameters
    @forward_property("_preset_list")
    def selected_preset():
        # type: () -> Optional[InstrumentPreset]
        pass

    @property
    def presets_path(self):
        # type: (AbstractInstrument) -> str
        """ overridden """
        return self.PRESETS_PATH

    @property
    def preset_name(self):
        # type: (AbstractInstrument) -> str
        """ overridden """
        return self.name

    def format_preset_name(self, preset_name):
        # type: (AbstractInstrument, str) -> str
        """ overridden """
        return preset_name

    def scroll_presets_or_samples(self, go_next):
        # type: (AbstractInstrument, bool) -> Sequence
        self.parent.navigationManager.show_device_view()

        seq = Sequence()
        seq.add(partial(self._preset_list.scroll, go_next=go_next))
        seq.add(partial(self._sync_selected_preset))
        return seq.done()

    def scroll_preset_categories(self, go_next):
        # type: (AbstractInstrument, bool) -> None
        if not len(self._preset_list.categories):
            raise Protocol0Warning("this instrument does not have categories")

        self.parent.navigationManager.show_device_view()
        self._preset_list.selected_category = scroll_values(
            self._preset_list.categories, self._preset_list.selected_category, go_next
        ).lower()
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            self.track.abstract_track.track_name.update()
        else:
            self.parent.show_message("selected preset category %s" % self._preset_list.selected_category.title())

    def _sync_selected_preset(self):
        # type: (AbstractInstrument) -> Sequence
        seq = Sequence()
        if self.selected_preset:
            if isinstance(self.device, PluginDevice):
                self.device.selected_preset_index = self.selected_preset.index
            seq.add(partial(self.load_preset, self.selected_preset))
            seq.add(partial(self.track.abstract_track.track_name.update, self.selected_preset.name))
        return seq.done()

    def load_preset(self, preset):
        # type: (AbstractInstrument, InstrumentPreset) -> Optional[Sequence]
        """ Overridden default is send program change """
        seq = Sequence()
        seq.add(self.track.abstract_track.arm)
        seq.add(partial(self.parent.midiManager.send_program_change, preset.index + self.PROGRAM_CHANGE_OFFSET))
        return seq.done()
