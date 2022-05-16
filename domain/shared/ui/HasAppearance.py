from typing import Protocol, runtime_checkable

from protocol0.domain.shared.ui.Refreshable import Refreshable


@runtime_checkable
class HasAppearance(Protocol):
    @property
    def appearance(self):
        # type: () -> Refreshable
        raise NotImplementedError
