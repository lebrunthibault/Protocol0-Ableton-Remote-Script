from typing_extensions import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.shared.observer.Observable import Observable


class Observer(Protocol):
    def update(self, observable):
        # type: (Observable) -> None
        pass
