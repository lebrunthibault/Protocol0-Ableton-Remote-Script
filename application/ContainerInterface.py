from typing import Type

from protocol0.shared.types import T


class ContainerInterface(object):
    def get(self, cls):
        # type: (Type[T]) -> T
        raise NotImplementedError
