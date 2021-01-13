class Protocol0Error(RuntimeError):
    def __init__(self, message):
        # type: (str) -> None

        from a_protocol_0 import Protocol0
        Protocol0.SELF.show_message(str(message))
        super(RuntimeError, self).__init__(str(message))
