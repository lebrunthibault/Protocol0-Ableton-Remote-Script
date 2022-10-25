from typing import Tuple


class MidiBytesSentEvent(object):
    def __init__(self, midi_bytes):
        # type: (Tuple) -> None
        self.midi_bytes = midi_bytes
