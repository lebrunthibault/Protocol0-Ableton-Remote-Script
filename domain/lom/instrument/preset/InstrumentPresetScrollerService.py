from functools import partial

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.decorators import lock
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentPresetScrollerService(object):
    @lock
    def scroll_presets_or_samples(self, instrument, go_next):
        # type: (InstrumentInterface, bool) -> Sequence
        ApplicationViewFacade.show_device()

        seq = Sequence()
        track = instrument.track.abstract_track
        if isinstance(track, ExternalSynthTrack) and not track.can_change_presets:
            seq.add(track.disable_protected_mode)
            return seq.done()

        seq.add(partial(instrument.scroll_presets, go_next))
        return seq.done()

    def scroll_preset_categories(self, instrument, go_next):
        # type: (InstrumentInterface, bool) -> None
        if not len(instrument.preset_list.categories):
            raise Protocol0Warning("this instrument does not have categories")

        ApplicationViewFacade.show_device()
        category = scroll_values(
            instrument.preset_list.categories, instrument.preset_list.selected_category, go_next
        ).lower()
        instrument.preset_list.set_selected_category(category)
        category = instrument.preset_list.selected_category.title()
        if instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            instrument.track.abstract_track.track_name.update(name=category)
        else:
            StatusBar.show_message("selected preset category %s" % category)
