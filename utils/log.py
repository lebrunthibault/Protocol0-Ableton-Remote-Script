import logging

from a_protocol_0.enums.LogLevelEnum import LogLevelEnum, ACTIVE_LOG_LEVEL

logger = logging.getLogger(__name__)


def log_ableton(message, debug=True, level=LogLevelEnum.DEV, direct_call=True, exclusive_log=False):
    # type: (str, bool) -> None
    """ a log function and not method allowing us to call this even with no access to the ControlSurface object """
    message = "%s: %s" % (LogLevelEnum(level).name.lower(), str(message))
    if any([not isinstance(param, bool) for param in [debug, direct_call, exclusive_log]]):
        log_ableton("log_ableton: parameter mismatch, logging anyway")
        debug = True
        direct_call = True
        exclusive_log = False
        message = locals().values()
    if debug:
        try:
            from a_protocol_0.utils.utils import get_frame_info
            frame_info = get_frame_info(2 if direct_call else 4)
            if frame_info:
                message = "%s (%s:%s in %s)" % (message, frame_info.filename, frame_info.line, frame_info.method_name)
        except Exception:
            pass
    if exclusive_log and ACTIVE_LOG_LEVEL != LogLevelEnum.EXCLUSIVE_LOG:
        return
    for line in message.splitlines():
        line = "P0 - %s" % str(line)
        logging.info(line)
        print(line)
