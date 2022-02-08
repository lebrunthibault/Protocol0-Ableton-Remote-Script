from typing import Type

from protocol0.shared.ContainerInterface import ContainerInterface
from protocol0.shared.my_types import T


class TestContainer(ContainerInterface):
    def get(self, cls):
        # type: (Type[T]) -> T
        raise None
