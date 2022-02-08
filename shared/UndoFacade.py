from typing import Callable, Optional


class UndoFacade(object):
    _INSTANCE = None  # type: Optional[UndoFacade]

    def __init__(self, begin_undo_step, end_undo_step):
        # type: (Callable, Callable) -> None
        UndoFacade._INSTANCE = self
        self._begin_undo_step = begin_undo_step
        self._end_undo_step = end_undo_step

    @classmethod
    def begin_undo_step(cls):
        # type: () -> None
        cls._INSTANCE._end_undo_step()

    @classmethod
    def end_undo_step(cls):
        # type: () -> None
        cls._INSTANCE._end_undo_step()
