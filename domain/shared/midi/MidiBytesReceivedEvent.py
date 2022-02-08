from typing import Tuple


class MidiBytesReceivedEvent(object):
    def __init__(self, midi_bytes):
        # type: (Tuple) -> None
        self.midi_bytes = midi_bytes
