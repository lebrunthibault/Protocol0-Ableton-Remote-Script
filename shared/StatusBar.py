class StatusBar(object):
    """ Facade for writing to the status bar """
    @classmethod
    def show_message(cls, message):
        # type: (str) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.show_message(message)
