from typing import Optional


class ErrorRaisedEvent(object):
    def __init__(self, context=None):
        # type: (Optional[str]) -> None
        self.context = context
