from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupPreset(AbstractActionGroup):
    """
    This manager is for unusual tasks.
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupPreset, self).__init__(channel=13, filter_active_tracks=False, *a, **k)
        # SCAN encoder
        self.add_encoder(identifier=1, name="scan (import) presets", on_press=self.parent.presetManager.refresh_presets)