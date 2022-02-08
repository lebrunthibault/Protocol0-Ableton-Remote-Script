from functools import partial

from typing import Optional, List, Any, Callable

from protocol0.application.faderfox.DoubleActionExecutionException import DoubleActionExecutionException
from protocol0.application.faderfox.EncoderMoveEnum import EncoderMoveEnum
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import get_callable_repr, is_lambda
from protocol0.shared.Logger import Logger
from protocol0.shared.UndoFacade import UndoFacade


class EncoderAction(object):
    def __init__(self, func, move_type, name, *a, **k):
        # type: (Callable, EncoderMoveEnum, Optional[str], Any, Any) -> None
        """
        base moves are listed in the enum. press is the default choice
        """
        super(EncoderAction, self).__init__(*a, **k)
        assert callable(func), "func action should be callable: %s" % get_callable_repr(func)
        self.func = func
        self.move_type = move_type
        self.name = name
        self._is_executing = False
        self.cancel_action = None  # type: Optional[EncoderAction]

    def __repr__(self, **k):
        # type: (Any) -> str
        return "%s : %s" % (self.name, get_callable_repr(self.func))

    def execute(self, encoder_name, *a, **k):
        # type: (str, Any, Any) -> Optional[Sequence]
        """
        NB : Here lambda is just a way to act on the right objects at runtime
            like this we can display the function name
        """
        if self._is_executing:
            self._is_executing = False
            if self.cancel_action:
                self.cancel_action.execute(encoder_name, *a, **k)
                return None
            raise DoubleActionExecutionException(self)

        UndoFacade.begin_undo_step()
        if is_lambda(self.func):
            func = self.func()  # allows delaying property lookup until execution time
        else:
            func = self.func
        if func is None:
            return None  # the action is sync and is already processed
        assert callable(func), "%s : action func should be callable, got %s" % (
            encoder_name,
            get_callable_repr(func),
        )
        if self.move_type != EncoderMoveEnum.SCROLL:
            Logger.log_info("%s : executing %s" % (encoder_name, get_callable_repr(func)))
        else:
            Logger.log_info("%s : scrolling %s" % (encoder_name, get_callable_repr(func)))

        self._is_executing = True
        seq = Sequence()

        # with Protocol0.SELF.component_guard():
        # todo: check
        seq.add(partial(func, *a, **k))
        seq.add(UndoFacade.end_undo_step)
        seq.on_end(partial(setattr, self, "_is_executing", False))
        return seq.done()

    @staticmethod
    @handle_error
    def make_actions(
            name,  # type: str
            on_press,  # type: Optional[Callable]
            on_cancel_press,  # type: Optional[Callable]
            on_long_press,  # type: Optional[Callable]
            on_cancel_long_press,  # type: Optional[Callable]
            on_scroll,  # type: Optional[Callable]
    ):
        # type: (...) -> List[EncoderAction]

        actions = []  # type: List[EncoderAction]
        if on_press:
            actions.append(EncoderAction(on_press, move_type=EncoderMoveEnum.PRESS, name=name))
        if on_cancel_press:
            if not on_press:
                raise Protocol0Error("Cannot set on_cancel_press without on_press")
            actions[-1].cancel_action = EncoderAction(on_cancel_press, move_type=EncoderMoveEnum.PRESS, name=name)
        if on_long_press:
            if not on_press:
                raise Protocol0Error("Cannot set on_long_press without on_press")
            actions.append(EncoderAction(on_long_press, move_type=EncoderMoveEnum.LONG_PRESS, name=name))  # type: ignore[arg-type]
        if on_cancel_long_press:
            if not on_long_press:
                raise Protocol0Error("Cannot set on_cancel_long_press without on_long_press")
            actions[-1].cancel_action = EncoderAction(on_cancel_long_press, move_type=EncoderMoveEnum.LONG_PRESS, name=name)
        if on_scroll:
            actions.append(EncoderAction(on_scroll, move_type=EncoderMoveEnum.SCROLL, name=name))  # type: ignore[arg-type]

        return actions
