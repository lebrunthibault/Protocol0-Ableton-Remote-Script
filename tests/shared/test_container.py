from typing import Any, Type, Dict

from protocol0.application.Container import Container


class ContainerTest(Container):
    # noinspection PyMissingConstructor
    def __init__(self):
        self._registry = {}  # type: Dict[Type, Any]


class Interface(object):
    pass


class Implementation(Interface):
    pass


def test_container():
    container = ContainerTest()
    service = Implementation()
    container._register(service)
    assert container.get(Implementation) == service
    assert container.get(Interface) == service
