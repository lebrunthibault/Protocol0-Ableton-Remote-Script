import collections
import json
import logging
import types

from typing import Optional, TYPE_CHECKING, Any, List, Tuple, Dict

from protocol0.config import Config
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.utils.utils import smart_string

if TYPE_CHECKING:
    from protocol0.enums.LogLevelEnum import LogLevelEnum  # noqa


def log_ableton(message, debug=True, level=None):
    # type: (Any, bool, Optional[LogLevelEnum]) -> None
    """ a log function and not method allowing us to call this even with no access to the ControlSurface object """
    if isinstance(message, types.GeneratorType):
        message = list(message)

    if isinstance(message, List) or isinstance(message, Dict):
        message = json.dumps(message, indent=4)

    if not isinstance(message, basestring):
        message = str(message)

    from protocol0.enums.LogLevelEnum import LogLevelEnum  # noqa
    level = level or LogLevelEnum.INFO
    if level.value < Config.LOG_LEVEL.value:
        return
    message = "%s: %s" % (level.name.lower(), smart_string(message))
    if not isinstance(debug, bool):
        raise Protocol0Error("log_ableton: parameter mismatch")
    if debug:
        from protocol0.utils.utils import get_frame_info

        frame_info = get_frame_info(4)
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
