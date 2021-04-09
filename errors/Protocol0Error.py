import traceback

from typing import Optional, List


class Protocol0Error(RuntimeError):
    def __init__(self, message, context=None, show_warning=True, exception=None):
        # type: (str, Optional[List], Exception) -> None

        from a_protocol_0 import Protocol0
        if show_warning:
            Protocol0.SELF.show_message(str(message))
        Protocol0.SELF.protocol0_song.handle_error(str(message))
        if context is not None and show_warning:
            Protocol0.SELF.log_error("Additional info : %s" % context)
        # raise exception or Exception(message)

        raise Exception(traceback.format_exc())