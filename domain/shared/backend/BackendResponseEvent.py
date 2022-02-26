from typing import Any


class BackendResponseEvent(object):
    def __init__(self, res):
        # type: (Any) -> None
        self.res = res
