from typing import Optional, List, Any, Callable, cast

from a_protocol_0.controls.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.controls.EncoderMoveEnum import EncoderMoveEnum
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import handle_error
from a_protocol_0.utils.utils import get_callable_name, is_lambda


class EncoderAction(AbstractObject):
    def __init__(self, func, move_type=None, modifier_type=None, *a, **k):
        # type: (Callable, Optional[EncoderMoveEnum], Optional[EncoderModifierEnum], Any, Any) -> None
        """
        base moves are listed in the enum. press is the default choice
        Any modifier can be applied to a press or long_press but only shift is available for scrolling for now
        """
        super(EncoderAction, self).__init__(*a, **k)
        assert callable(func), "func action should be callable: %s" % get_callable_name(func)
        self.func = func
        self.move_type = cast(EncoderMoveEnum, move_type or EncoderMoveEnum.PRESS)
        self.modifier_type = modifier_type

    def __repr__(self):
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
        func = self.func() if is_lambda(self.func) else self.func
        if func is None:
            self.parent.show_message("Action empty")
            return
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
        on_press=None,
        on_long_press=None,
        on_shift_press=None,
        on_shift_long_press=None,
        on_scroll=None,
        on_shift_scroll=None,
    ):
        """ This is not necessary but makes it more convenient to define most encoder actions. """
        actions = []  # type: List[EncoderAction]
        if on_press:
            actions.append(EncoderAction(on_press))
        if on_long_press:
            actions.append(EncoderAction(on_long_press, move_type=EncoderMoveEnum.LONG_PRESS))
        if on_shift_press:
            actions.append(EncoderAction(on_shift_press, modifier_type=EncoderModifierEnum.SHIFT))
        if on_shift_long_press:
            actions.append(
                EncoderAction(
                    on_shift_long_press,
                    move_type=EncoderMoveEnum.LONG_PRESS,
                    modifier_type=EncoderModifierEnum.SHIFT,
                )
            )
        if on_scroll:
            actions.append(EncoderAction(on_scroll, move_type=EncoderMoveEnum.SCROLL))
        if on_shift_scroll:
            actions.append(
                EncoderAction(
                    on_shift_scroll, move_type=EncoderMoveEnum.SCROLL, modifier_type=EncoderModifierEnum.SHIFT
                )
            )

        return actions
