from abc import abstractmethod

from protocol0.domain.lom.Listenable import Listenable
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.infra.scheduler.Scheduler import Scheduler


class AbstractObjectName(Listenable):
    @abstractmethod
    def update(self):
        # type: () -> str
        raise NotImplementedError

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        Scheduler.defer(self.update)
