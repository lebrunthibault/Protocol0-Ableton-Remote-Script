import sys

import win32com.client

from utils import setup_logs, log

shell = win32com.client.Dispatch("WScript.Shell")


if __name__ == "__main__":
    setup_logs()
    keys = sys.argv[1]
    log("sending keys: %s" % keys)
    shell.SendKeys(keys, 0)
