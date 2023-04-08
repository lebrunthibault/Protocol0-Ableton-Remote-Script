from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import (
    InstrumentPresetScrollerService,
)
from protocol0.shared.Song import Song


class ActionGroupPreset(ActionGroupInterface):
    def configure(self):
        # type: () -> None
        # PREset encoder
        self.add_encoder(
            identifier=1,
            name="scroll presets",
            filter_active_tracks=True,
            on_scroll=lambda: partial(
                self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples,
                Song.current_track(),
            ),
        )

        # CATegory encoder
        self.add_encoder(
            identifier=2,
            name="scroll preset categories",
            on_scroll=lambda: partial(
                self._container.get(InstrumentPresetScrollerService).scroll_preset_categories,
                Song.current_track(),
            ),
        )
