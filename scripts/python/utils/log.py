import os
import sys
from datetime import datetime

# noinspection PyUnresolvedReferences
import wmi

LOG_DIRECTORY = "C:\\Users\\thiba\\OneDrive\\Documents\\protocol0_logs"


def _get_log_filename():
    # type: () -> str
    return os.path.join(LOG_DIRECTORY, os.path.basename(sys.argv[0])).replace(".py", ".txt")


def setup_logs():
    # type: () -> None
    if os.path.exists(_get_log_filename()):
        os.remove(_get_log_filename())


def log(message):
    # type: (str) -> None
    """ expecting sequential script execution """
    message = "%s : %s\n" % (datetime.now(), message)
    print(message)
    with open(_get_log_filename(), "a") as f:
        f.write(message)
