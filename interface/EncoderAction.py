from typing import Optional, List, Any, Callable

from a_protocol_0.interface.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.interface.EncoderMoveEnum import EncoderMoveEnum
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import handle_error
from a_protocol_0.utils.utils import get_callable_name, is_lambda


class EncoderAction(AbstractObject):
    def __init__(self, func, move_type=EncoderMoveEnum.PRESS, modifier_type=None, *a, **k):
        # type: (Callable, EncoderMoveEnum, Optional[EncoderModifierEnum], Any, Any) -> None
        """
        base moves are listed in the enum. press is the default choice
        Any modifier can be applied to a press or long_press but only shift is available for scrolling for now
        """
        super(EncoderAction, self).__init__(*a, **k)
        assert callable(func), "func action should be callable: %s" % get_callable_name(func)
        self.func = func
        self.move_type = move_type
        self.modifier_type = modifier_type

    def __repr__(self):
        # type: () -> str
        move = self.move_type.value + ("(%s)" % self.modifier_type.value if self.modifier_type else "")
        return "%s : %s" % (move, get_callable_name(self.func))

    @handle_error
    def execute(self, encoder_name, *a, **k):
        # type: (str, Any, Any) -> None
        """
        NB : Here lambda is just a way to act on the right objects at runtime
            like this we can display the function name
        """
        self.song.begin_undo_step()
        if is_lambda(self.func):
            func = self.func()  # allows delaying property lookup until execution time
        else:
            func = self.func
        if func is None:
            return  # the action is sync and is already processed
        assert callable(func), "%s : action func should be callable, got %s" % (
            encoder_name,
            get_callable_name(func),
        )
        if self.move_type != EncoderMoveEnum.SCROLL:
            self.parent.log_notice("%s : executing %s" % (encoder_name, get_callable_name(func)))

        func(*a, **k)
        self.song.end_undo_step()

    @staticmethod
    def make_actions(
        on_press=None,  # type: Optional[Callable]
        on_long_press=None,  # type: Optional[Callable]
        on_scroll=None,  # type: Optional[Callable]
    ):
        # type: (...) -> List[EncoderAction]
        """ This is not necessary but makes it more convenient to define most encoder actions. """
        actions = []  # type: List[EncoderAction]
        if on_press:
            actions.append(EncoderAction(on_press))
        if on_long_press:
            actions.append(EncoderAction(on_long_press, move_type=EncoderMoveEnum.LONG_PRESS))  # type: ignore[arg-type]
        if on_scroll:
            actions.append(EncoderAction(on_scroll, move_type=EncoderMoveEnum.SCROLL))  # type: ignore[arg-type]

        return actions
