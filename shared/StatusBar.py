class StatusBar(object):
    """ Facade for writing to the status bar """
    @classmethod
    def show_message(cls, message, log=True):
        # type: (str, bool) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.show_message(message, log=log)
