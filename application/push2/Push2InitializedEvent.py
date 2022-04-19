from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0_push2.push2 import Push2


class Push2InitializedEvent(object):
    def __init__(self, push2):
        # type: (Push2) -> None
        self.push2 = push2
