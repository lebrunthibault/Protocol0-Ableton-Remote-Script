from functools import partial

from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import InstrumentPresetScrollerService
from protocol0.domain.lom.instrument.preset.PresetService import PresetService
from protocol0.shared.SongFacade import SongFacade


class ActionGroupPreset(ActionGroupMixin):
    CHANNEL = 13

    def configure(self):
        # type: () -> None
        # PREset encoder
        self.add_encoder(
            identifier=1,
            name="scroll presets",
            filter_active_tracks=True,
            on_scroll=lambda: partial(self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples,
                                      SongFacade.current_instrument()),
        )

        # CATegory encoder
        self.add_encoder(
            identifier=2, name="scroll preset categories",
            on_scroll=lambda: partial(self._container.get(InstrumentPresetScrollerService).scroll_preset_categories,
                                      SongFacade.current_instrument()),
        )

        # SCAN encoder
        self.add_encoder(identifier=16, name="scan (import) all track presets",
                         on_press=self._container.get(PresetService).refresh_presets)
