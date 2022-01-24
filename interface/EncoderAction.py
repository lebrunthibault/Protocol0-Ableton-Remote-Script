from functools import partial

from typing import Optional, List, Any, Callable

from protocol0.errors.DoubleEncoderActionExecution import DoubleEncoderActionExecution
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.interface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import get_callable_repr, is_lambda


class EncoderAction(AbstractObject):
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
        self.executing = False
        self.cancel_action = None  # type: Optional[EncoderAction]

    def __repr__(self, **k):
        # type: (Any) -> str
        move = self.move_type.name
        return "%s : %s" % (move, get_callable_repr(self.func))

    def execute(self, encoder_name, *a, **k):
        # type: (str, Any, Any) -> Optional[Sequence]
        """
        NB : Here lambda is just a way to act on the right objects at runtime
            like this we can display the function name
        """
        if self.executing:
            if self.cancel_action:
                return self.cancel_action.execute(encoder_name, *a, **k)
            raise DoubleEncoderActionExecution(self)
        if self.song:
            self.song.begin_undo_step()
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
            self.parent.log_notice("%s : executing %s" % (encoder_name, get_callable_repr(func)))
        else:
            self.parent.log_notice("%s : scrolling %s" % (encoder_name, get_callable_repr(func)))

        self.executing = True
        seq = Sequence()
        with self.parent.component_guard():
            seq.add(partial(func, *a, **k))
            if self.song:
                seq.add(self.song.end_undo_step)
            seq.add(partial(setattr, self, "executing", False))
        return seq.done()

    @staticmethod
    def make_actions(
            name,  # type: str
            on_press,  # type: Optional[Callable]
            on_cancel_press,  # type: Optional[Callable]
            on_long_press,  # type: Optional[Callable]
            on_scroll,  # type: Optional[Callable]
    ):
        # type: (...) -> List[EncoderAction]

        actions = []  # type: List[EncoderAction]
        if on_press:
            actions.append(EncoderAction(on_press, move_type=EncoderMoveEnum.PRESS, name=name))
        if on_cancel_press:
            if not on_press:
                raise Protocol0Error("Cannot set on_cancel_press without on_press")
            actions[0].cancel_action = EncoderAction(on_cancel_press, move_type=EncoderMoveEnum.PRESS, name=name)
        if on_long_press:
            if not on_press:
                raise Protocol0Error("Cannot set on_long_press without on_press")
            actions.append(EncoderAction(on_long_press, move_type=EncoderMoveEnum.LONG_PRESS, name=name))  # type: ignore[arg-type]
        if on_scroll:
            actions.append(EncoderAction(on_scroll, move_type=EncoderMoveEnum.SCROLL, name=name))  # type: ignore[arg-type]

        return actions
