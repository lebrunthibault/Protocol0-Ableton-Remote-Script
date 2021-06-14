from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(id=1, name="test", on_press=self.action_test)

    def action_test(self):
        # type: () -> None
        res = self.system.reload_ableton()
        self.parent.log_dev(res)
