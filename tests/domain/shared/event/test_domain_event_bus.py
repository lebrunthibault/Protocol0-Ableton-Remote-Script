from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent


def test_domain_event_bus():
    test_res = []

    def listener(_):
        test_res.append(True)

    DomainEventBus.subscribe(BarEndingEvent, listener)
    DomainEventBus.emit(BarEndingEvent())

    assert test_res == [True]


class TestEvent(object):
    pass


def sub():
    pass


def test_domain_event_bus_duplicate():
    DomainEventBus._registry = {}
    DomainEventBus.subscribe(TestEvent, sub)
    assert DomainEventBus._registry[TestEvent] == [sub]

    # no duplicates
    DomainEventBus.subscribe(TestEvent, sub)
    assert DomainEventBus._registry[TestEvent] == [sub]


class Test(object):
    def m(self):
        pass


def test_domain_event_bus_duplicate_methods():
    DomainEventBus._registry = {}
    t1, t2 = Test(), Test()
    DomainEventBus.subscribe(TestEvent, t1.m)
    assert DomainEventBus._registry[TestEvent] == [t1.m]

    # no duplicates across classes
    DomainEventBus.subscribe(TestEvent, t2.m, unique_method=True)
    assert DomainEventBus._registry[TestEvent] == [t1.m]
