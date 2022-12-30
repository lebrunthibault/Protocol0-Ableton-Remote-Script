from functools import partial

from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentPresetScrollerService(object):
    @lock
    def scroll_presets_or_samples(self, track, go_next):
        # type: (AbstractTrack, bool) -> Sequence
        assert track.instrument, "track has not instrument"
        ApplicationViewFacade.show_device()

        seq = Sequence()
        if isinstance(track, ExternalSynthTrack) and not track.can_change_presets:
            seq.add(track.disable_protected_mode)
            return seq.done()

        seq.add(partial(track.scroll_presets, go_next))
        return seq.done()

    def scroll_preset_categories(self, track, go_next):
        # type: (AbstractTrack, bool) -> None
        assert track.instrument, "track has not instrument"
        instrument = track.instrument

        if not len(instrument.preset_list.categories):
            raise Protocol0Warning("this instrument does not have categories")

        ApplicationViewFacade.show_device()
        category = ValueScroller.scroll_values(
            instrument.preset_list.categories, instrument.preset_list.selected_category, go_next
        ).lower()
        instrument.preset_list.set_selected_category(category)
        category = instrument.preset_list.selected_category.title()
        if instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            track.appearance.name = category
        else:
            StatusBar.show_message("selected preset category %s" % category)
