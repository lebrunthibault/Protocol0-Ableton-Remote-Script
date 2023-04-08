from protocol0.application.command.SerializableCommand import SerializableCommand


class MidiNoteCommand(SerializableCommand):
    def __init__(self, channel, note):
        # type: (int, int) -> None
        super(MidiNoteCommand, self).__init__()
        self.channel = channel
        self.note = note
