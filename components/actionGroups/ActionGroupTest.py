from protocol0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from typing import Any


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(id=1, name="test", on_press=self.action_test)

    def action_test(self):
        # type: () -> None
        self.system.health()
