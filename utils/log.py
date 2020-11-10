import logging

from ClyphX_Pro.clyphx_pro.user_actions.utils.config import Config

if Config.DEBUG:
    logging.basicConfig(filename="C:/Users/thiba/AppData/Roaming/Ableton/Live 10.1.25/Preferences/Log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def log_ableton(message):
    if Config.DEBUG:
        logging.info(message)
