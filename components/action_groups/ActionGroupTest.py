from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.interface.InterfaceState import InterfaceState


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)

    def action_test(self):
        # type: () -> None
        self.parent.log_info(InterfaceState.SELECTED_RECORDING_BAR_LENGTH)
