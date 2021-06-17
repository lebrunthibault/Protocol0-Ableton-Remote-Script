import os

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
        from websocket import create_connection

        ws = create_connection(os.getenv("WEBSOCKET_URL"))
        self.parent.log_dev("Sending 'Hello, World'...")
        ws.send("Hello, World")
        self.parent.log_dev("Sent")
        self.parent.log_dev("Receiving...")
        result = ws.recv()
        self.parent.log_dev("Received '%s'" % result)
        ws.close()
