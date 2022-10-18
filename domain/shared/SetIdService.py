from uuid import uuid4

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class SetIdService(object):
    def __init__(self):
        # type: () -> None
        self._id = str(uuid4())

        Backend.client().register_set(self._id)

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

    def get_id(self):
        # type: () -> str
        return self._id

    def _disconnect(self):
        # type: () -> None
        Backend.client().remove_set(self._id)
