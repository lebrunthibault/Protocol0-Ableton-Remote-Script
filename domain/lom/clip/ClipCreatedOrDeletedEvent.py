from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot


class ClipCreatedOrDeletedEvent(object):
    def __init__(self, clip_slot):
        # type: (ClipSlot) -> None
        self.clip_slot = clip_slot

    def target(self):
        # type: () -> object
        return self.clip_slot
