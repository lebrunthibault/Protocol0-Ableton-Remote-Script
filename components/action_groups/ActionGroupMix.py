from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupMix(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMix, self).__init__(channel=6, *a, **k)
        # CHecK encoder
        self.add_encoder(identifier=1, name="check clipping tracks",
                         on_press=self.parent.mixingManager.toggle_volume_check)

        # FIX encoder
        self.add_encoder(identifier=2, name="scroll all tracks volume",
                         on_scroll=self.parent.trackManager.scroll_all_tracks_volume)

