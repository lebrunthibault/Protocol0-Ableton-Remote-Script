from typing import Optional, List


class Protocol0Error(RuntimeError):
    def __init__(self, message, context=None, log_error=True):
        # type: (str, Optional[List]) -> None

        from a_protocol_0 import Protocol0
        if log_error:
            Protocol0.SELF.show_message(str(message))
        super(RuntimeError, self).__init__(str(message))
        if context is not None and log_error:
            Protocol0.SELF.log_error("Additional info : %s" % context)
