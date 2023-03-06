from typing import Any


class BackendEvent(object):
    def __init__(self, event, data=None):
        # type: (str, Any) -> None
        self.event = event
        self.data = data
