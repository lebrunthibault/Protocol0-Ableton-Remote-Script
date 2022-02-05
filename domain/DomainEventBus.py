from functools import partial

from typing import Dict, List, Type, Callable

from protocol0.domain.DomainEventInterface import DomainEventInterface
from protocol0.domain.sequence.Sequence import Sequence


class DomainEventBus(object):
    _registry = {}  # type: Dict[Type[DomainEventInterface], List[Callable]]

    @classmethod
    def subscribe(cls, domain_event, subscriber):
        # type: (Type[DomainEventInterface], Callable) -> None
        if domain_event not in cls._registry:
            cls._registry[domain_event] = []

        if subscriber not in cls._registry[domain_event]:
            cls._registry[domain_event].append(subscriber)

    @classmethod
    def un_subscribe(cls, domain_event, subscriber):
        # type: (Type[DomainEventInterface], Callable) -> None
        if domain_event in cls._registry and subscriber in cls._registry[domain_event]:
            cls._registry[domain_event].remove(subscriber)

    @classmethod
    def notify(cls, domain_event):
        # type: (DomainEventInterface) -> Sequence
        seq = Sequence()
        if type(domain_event) in cls._registry:
            for subscriber in cls._registry[type(domain_event)]:
                seq.add(partial(subscriber, domain_event))

        return seq.done()
