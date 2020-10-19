import logging

logging.basicConfig(filename="C:/Users/thiba/AppData/Roaming/Ableton/Live 10.1.18/Preferences/Log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def log_ableton(message):
    logging.info(message)
