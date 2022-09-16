import time
from functools import partial

from typing import Optional, List, Any, Callable

from protocol0.application.control_surface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.func import get_callable_repr, is_lambda
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class EncoderAction(object):
    def __init__(self, func, move_type, name):
        # type: (Callable, EncoderMoveEnum, Optional[str]) -> None
        """
        base moves are listed in the enum. press is the default choice
        """
        super(EncoderAction, self).__init__()
        assert callable(func), "func action should be callable: %s" % get_callable_repr(func)
        self.func = func
        self.move_type = move_type
        self.name = name

    def __repr__(self, **k):
        # type: (Any) -> str
        return "%s : %s" % (self.name, get_callable_repr(self.func))

    def execute(self, encoder_name, *a, **k):
        # type: (str, Any, Any) -> Optional[Sequence]
        """
        NB : Here lambda is just a way to act on the right objects at runtime
            like this we can display the function name
        """
        UndoFacade.begin_undo_step()
        if is_lambda(self.func):
            func = self.func()  # allows delaying property lookup until execution time
        else:
            func = self.func
        if func is None:
            return None  # the action is sync and is already processed

        func_name = get_callable_repr(func)
        assert callable(func), "%s : action func should be callable, got %s" % (
            encoder_name,
            func_name,
        )
        start_at = time.time()
        seq = Sequence()
        seq.add(partial(func, *a, **k))
        seq.add(UndoFacade.end_undo_step)

        if self.move_type != EncoderMoveEnum.SCROLL:
            seq.add(lambda: Logger.info("%s : took %.3fs" % (func_name, time.time() - start_at)))

        return seq.done()

    @classmethod
    def make_actions(cls, name, on_press, on_long_press, on_scroll):
        # type: (str, Optional[Callable], Optional[Callable], Optional[Callable]) -> List[EncoderAction]

        actions = []  # type: List[EncoderAction]
        if on_press:
            actions.append(EncoderAction(on_press, move_type=EncoderMoveEnum.PRESS, name=name))
        if on_long_press:
            if not on_press:
                raise Protocol0Error("Cannot set on_long_press without on_press")
            actions.append(
                EncoderAction(on_long_press, move_type=EncoderMoveEnum.LONG_PRESS, name=name)
            )
        if on_scroll:
            actions.append(EncoderAction(on_scroll, move_type=EncoderMoveEnum.SCROLL, name=name))

        return actions
