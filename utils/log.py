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
    if any([not isinstance(param, bool) for param in [debug, direct_call, exclusive_log]]):
        log_ableton("log_ableton: parameter mismatch, logging anyway")
        debug = True
        direct_call = True
        exclusive_log = False
        message = locals().values()
    if debug:
        try:
            frame_info = get_frame_info(2 if direct_call else 4)
            if frame_info:
                message = "%s (%s:%s in %s)" % (message, frame_info.filename, frame_info.line, frame_info.method_name)
        except Exception:
            pass
    if exclusive_log and LogLevel.ACTIVE_LOG_LEVEL != LogLevel.EXCLUSIVE_LOG:
        return
    for line in message.splitlines():
        line = "P0 - %s" % str(line)
        logging.info(line)
        print(line)


@contextmanager
def set_object_attr(obj, attr, value):
    if not hasattr(obj, attr):
        raise RuntimeError("object %s has not specified attr : %s" % (obj, attr))
    previous_value = getattr(obj, attr)
    setattr(obj, attr, value)
    yield
    setattr(obj, attr, previous_value)
