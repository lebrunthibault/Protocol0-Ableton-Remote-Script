import logging
import os
from os.path import expanduser

from ClyphX_Pro.clyphx_pro.user_actions.utils.config import Config

if Config.DEBUG:
    home = expanduser("~")
    abletonVersion = os.getenv("abletonVersion")
    logging.basicConfig(filename=home + "/AppData/Roaming/Ableton/Live " + abletonVersion + "/Preferences/Log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def log(message):
    if Config.DEBUG:
        logging.info(message)
