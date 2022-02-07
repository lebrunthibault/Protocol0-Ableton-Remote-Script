import inspect
from functools import partial

from typing import Dict, List, Type, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.sequence.Sequence import Sequence  # noqa


class DomainEventBus(object):
    _registry = {}  # type: Dict[Type, List[Callable]]

    @classmethod
    def subscribe(cls, domain_event, subscriber):
        # type: (Type, Callable) -> None
        args = inspect.getargspec(subscriber).args
        if "self" in args:
            args = args[1:]
        assert len(args) == 1, "The subscriber should have a unique parameter for the event : %s" % subscriber

        if domain_event not in cls._registry:
            cls._registry[domain_event] = []

        if subscriber not in cls._registry[domain_event]:
            cls._registry[domain_event].append(subscriber)

    @classmethod
    def un_subscribe(cls, domain_event, subscriber):
        # type: (Type, Callable) -> None
        if domain_event in cls._registry and subscriber in cls._registry[domain_event]:
            cls._registry[domain_event].remove(subscriber)

    @classmethod
    def notify(cls, domain_event):
        # type: (object) -> Sequence
        from protocol0.domain.sequence.Sequence import Sequence  # noqa

        seq = Sequence()
        if type(domain_event) in cls._registry:
            for subscriber in cls._registry[type(domain_event)]:
                seq.add(partial(subscriber, domain_event))

        return seq.done()
