from protocol0.application.system_command.SerializableCommand import SerializableCommand


class CommandBusInterface(object):
    @classmethod
    def execute_from_string(cls, command_string):
        # type: (str) -> None
        raise NotImplementedError

    @classmethod
    def dispatch(cls, command):
        # type: (SerializableCommand) -> None
        raise NotImplementedError
