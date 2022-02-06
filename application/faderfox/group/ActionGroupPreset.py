from functools import partial

from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.shared.SongFacade import SongFacade


class ActionGroupPreset(ActionGroupMixin):
    CHANNEL = 2

    def configure(self):
        # type: () -> None
        # SCAN encoder
        self.add_encoder(identifier=1, name="scan (import) all track presets",
                         on_press=self._container.preset_manager.refresh_presets)

        # CATegory encoder
        self.add_encoder(
            identifier=2, name="scroll preset categories",
            on_scroll=lambda: partial(self._container.instrument_preset_scroller_manager.scroll_preset_categories, SongFacade.current_track().instrument),
        )
