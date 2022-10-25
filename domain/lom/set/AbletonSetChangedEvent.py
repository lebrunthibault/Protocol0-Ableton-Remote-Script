from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.set.AbletonSet import AbletonSet


class AbletonSetChangedEvent(object):
    def __init__(self, ableton_set):
        # type: (AbletonSet) -> None
        self.set = ableton_set
