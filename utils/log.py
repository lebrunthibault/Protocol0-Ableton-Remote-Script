import logging
import os
from os.path import expanduser

home = expanduser("~")
abletonVersion = os.getenv("abletonVersion")
logging.basicConfig(filename=home + "/AppData/Roaming/Ableton/Live " + abletonVersion + "/Preferences/Log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def log_ableton(message):
    logging.info(message)
