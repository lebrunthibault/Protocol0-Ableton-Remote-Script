from typing import TYPE_CHECKING

from protocol0.errors.Protocol0Warning import Protocol0Warning

if TYPE_CHECKING:
    from protocol0.interface.EncoderAction import EncoderAction


class DoubleEncoderActionExecution(Protocol0Warning):
    def __init__(self, encoder_action):
        # type: (EncoderAction) -> None
        message = "%s didn't finish" % encoder_action
        super(Protocol0Warning, self).__init__(message)
