from functools import partial

from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerManager import InstrumentPresetScrollerManager
from protocol0.domain.lom.instrument.preset.PresetManager import PresetManager
from protocol0.shared.SongFacade import SongFacade


class ActionGroupPreset(ActionGroupMixin):
    CHANNEL = 2

    def configure(self):
        # type: () -> None
        # SCAN encoder
        self.add_encoder(identifier=1, name="scan (import) all track presets",
                         on_press=self._container.get(PresetManager).refresh_presets)

        # CATegory encoder
        self.add_encoder(
            identifier=2, name="scroll preset categories",
            on_scroll=lambda: partial(self._container.get(InstrumentPresetScrollerManager).scroll_preset_categories, SongFacade.current_track().instrument),
        )
