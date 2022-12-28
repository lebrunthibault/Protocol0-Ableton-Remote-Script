from typing import Any, Optional


class BackendResponseEvent(object):
    def __init__(self, res, res_type):
        # type: (Any, Optional[str]) -> None
        self.res = res
        self.type = res_type
