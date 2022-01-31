from typing import Any

from protocol0.application.faderfox.group.AbstractActionGroup import AbstractActionGroup


class ActionGroupMix(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMix, self).__init__(channel=6, *a, **k)
        # CHecK encoder
        self.add_encoder(identifier=1, name="check clipping tracks",
                         on_press=self.parent.mixingManager.toggle_volume_check)
