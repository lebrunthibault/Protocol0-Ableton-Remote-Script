import inspect
import logging
import os
from os.path import expanduser

from a_protocol_0.consts import PROTOCOL0_FOLDER, REMOTE_SCRIPTS_FOLDER, LogLevel

home = expanduser("~")
abletonVersion = os.getenv("abletonVersion")
logging.basicConfig(filename=home + "/AppData/Roaming/Ableton/Live " + abletonVersion + "/Preferences/Log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def log_ableton(message, debug=True, direct_call=True, exclusive_log=False):
    # type: (str, bool) -> None
    if debug:
        try:
            call_frame = inspect.currentframe().f_back if direct_call else inspect.currentframe().f_back.f_back.f_back
            (filename, line, method, _, _) = inspect.getframeinfo(call_frame)
            filename = filename.replace(PROTOCOL0_FOLDER + "\\", "").replace(REMOTE_SCRIPTS_FOLDER + "\\", "")
            message = "%s (%s:%s in %s)" % (message, filename, line, method)
        except Exception:
            pass
    if exclusive_log and LogLevel.ACTIVE_LOG_LEVEL != LogLevel.EXCLUSIVE_LOG:
        return
    logging.info(message)


class ExclusiveLogContextManager(object):
    current_log_level = None

    def __enter__(self):
        self.current_log_level = LogLevel.ACTIVE_LOG_LEVEL
        LogLevel.ACTIVE_LOG_LEVEL = LogLevel.EXCLUSIVE_LOG

    def __exit__(self, type, value, traceback):
        LogLevel.ACTIVE_LOG_LEVEL = self.current_log_level
