from typing import List

from protocol0.shared.observer.Observer import Observer


class Observable(object):
    def __init__(self):
        # type: () -> None
        self._observers = []  # type: List[Observer]

    def register_observer(self, observer):
        # type: (Observer) -> None
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        # type: (Observer) -> None
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        # type: () -> None
        for observer in self._observers:
            observer.update(self)
