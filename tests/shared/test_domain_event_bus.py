from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent


def test_domain_event_bus():
    test_res = []

    def listener(_):
        test_res.append(True)

    DomainEventBus.subscribe(BarEndingEvent, listener)
    DomainEventBus.notify(BarEndingEvent())

    assert test_res == [True]
