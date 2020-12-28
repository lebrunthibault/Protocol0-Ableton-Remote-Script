import logging
import os
import sys
from contextlib import contextmanager
from os.path import expanduser

from a_protocol_0.consts import LogLevel
from a_protocol_0.utils.utils import get_frame_info

home = expanduser("~")
abletonVersion = os.getenv("abletonVersion")
log_file = "Log.txt" if sys.modules["Live"] else "Log-external.txt"
logging.basicConfig(filename=home + "/AppData/Roaming/Ableton/Live " + abletonVersion + "/Preferences/" + log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def log_ableton(message, debug=True, direct_call=True, exclusive_log=False):
    # type: (str, bool) -> None
    if not isinstance(debug, bool):
        raise RuntimeError("log_ableton: parameter mismatch")
    if debug:
        try:
            func_info = get_frame_info(1 if direct_call else 3)
            if func_info:
                (filename, line, method) = func_info
                message = "%s (%s:%s in %s)" % (message, filename, line, method)
        except Exception:
            pass
    if exclusive_log and LogLevel.ACTIVE_LOG_LEVEL != LogLevel.EXCLUSIVE_LOG:
        return
    logging.info(message)


@contextmanager
def set_object_attr(obj, attr, value):
    if not hasattr(obj, attr):
        raise RuntimeError("object %s has not specified attr : %s" % (obj, attr))
    previous_value = getattr(obj, attr)
    setattr(obj, attr, value)
    yield
    setattr(obj, attr, previous_value)
