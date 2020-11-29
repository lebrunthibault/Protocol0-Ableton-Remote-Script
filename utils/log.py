import logging
import os
from os.path import expanduser

from a_protocol_0.utils.config import Config

if Config.DEBUG:
    home = expanduser("~")
    abletonVersion = os.getenv("abletonVersion")
    logging.basicConfig(filename=home + "/AppData/Roaming/Ableton/Live " + abletonVersion + "/Preferences/Log.txt",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)


def log_ableton(message):
    if Config.DEBUG:
        logging.info(message)
