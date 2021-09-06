import logging

from protocol0.config import Config
from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.utils.utils import smart_string


def log_ableton(message, debug=True, level=LogLevelEnum.DEV, direct_call=True):
    # type: (basestring, bool, LogLevelEnum, bool) -> None
    """ a log function and not method allowing us to call this even with no access to the ControlSurface object """
    message = "%s: %s" % (LogLevelEnum(level).name.lower(), smart_string(message))
    if any(not isinstance(param, bool) for param in [debug, direct_call]):
        raise Protocol0Error("log_ableton: parameter mismatch")
    if debug:
        from protocol0.utils.utils import get_frame_info

        frame_info = get_frame_info(2 if direct_call else 4)
        if frame_info:
            message = "%s (%s:%s in %s)" % (
                message,
                frame_info.filename,
                frame_info.line,
                frame_info.method_name,
            )
    for line in message.splitlines():
        line = "P0 - %s" % line.decode("utf-8").encode("ascii", "replace")
        logging.info(line)
        print(line)
