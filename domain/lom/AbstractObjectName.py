from abc import abstractmethod

from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.shared.decorators import p0_subject_slot


class AbstractObjectName(AbstractObject):
    @abstractmethod
    def update(self):
        # type: () -> str
        raise NotImplementedError

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        self.parent.defer(self.update)
