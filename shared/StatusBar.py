from protocol0.shared.Logger import Logger


class StatusBar(object):
    """ Facade for writing to the status bar """
    @classmethod
    def show_message(cls, message):
        # type: (str) -> None
        from protocol0.application.Protocol0 import Protocol0
        # noinspection PyBroadException
        try:
            Protocol0.SHOW_MESSAGE(str(message))
        except Exception:
            Logger.log_warning("Couldn't show message : %s" % message)
