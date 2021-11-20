from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupPreset(AbstractActionGroup):
    """
    This manager is for unusual tasks.
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupPreset, self).__init__(channel=2, *a, **k)
        # SCAN encoder
        self.add_encoder(identifier=1, name="scan (import) all track presets",
                         on_press=self.parent.presetManager.refresh_presets)

        # CATegory encoder
        self.add_encoder(
            identifier=2, name="scroll preset categories", on_scroll=lambda: self.song.current_track.scroll_preset_categories
        )

