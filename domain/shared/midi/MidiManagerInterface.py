class MidiManagerInterface(object):
    def send_program_change(self, value, channel=0):
        # type: (int, int) -> None
        pass

    def pong_from_midi_server(self):
        # type: () -> None
        pass
