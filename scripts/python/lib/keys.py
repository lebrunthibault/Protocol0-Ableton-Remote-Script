import logging

import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")


def send_keys(keys: str) -> None:
    logging.info("sending keys: %s" % keys)
    shell.SendKeys(keys, 0)
