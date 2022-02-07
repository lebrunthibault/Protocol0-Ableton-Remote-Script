from functools import partial

from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.StatusBar import StatusBar


class InstrumentPresetScrollerManager(object):
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    PROGRAM_CHANGE_OFFSET = 0  # if we store presets not at the beginning of the list

    def scroll_presets_or_samples(self, instrument, go_next):
        # type: (InstrumentInterface, bool) -> Sequence
        ApplicationView.show_device()

        seq = Sequence()
        if not instrument.can_change_presets:
            seq.add(self._disable_protected_mode)

        seq.add(partial(instrument.preset_list.scroll, go_next=go_next))
        seq.add(partial(self._sync_selected_preset, instrument))
        return seq.done()

    def _disable_protected_mode(self, instrument):
        # type: (InstrumentInterface) -> Sequence
        seq = Sequence()
        seq.prompt("Disable protected mode ?")
        seq.add(partial(setattr, instrument, "protected_mode_active", False))
        seq.add(partial(StatusBar.show_message, "track protected mode disabled"))
        return seq.done()

    def scroll_preset_categories(self, instrument, go_next):
        # type: (InstrumentInterface, bool) -> None
        if not len(instrument.preset_list.categories):
            raise Protocol0Warning("this instrument does not have categories")

        ApplicationView.show_device()
        instrument.preset_list.selected_category = scroll_values(
            instrument.preset_list.categories, instrument.preset_list.selected_category, go_next
        ).lower()
        if instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            instrument.track.abstract_track.track_name.update()
        else:
            StatusBar.show_message("selected preset category %s" % instrument.preset_list.selected_category.title())

    def _sync_selected_preset(self, instrument):
        # type: (InstrumentInterface) -> Sequence
        seq = Sequence()
        if instrument.selected_preset:
            if isinstance(instrument.device, PluginDevice):
                instrument.device.selected_preset_index = instrument.selected_preset.index
            seq.add(instrument.track.abstract_track.arm)
            seq.add(partial(instrument.load_preset, instrument.selected_preset))
            seq.add(partial(instrument.track.abstract_track.track_name.update, instrument.selected_preset.name))
        return seq.done()
