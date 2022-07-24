import Live

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.string import smart_string
from protocol0.shared.sequence.Sequence import Sequence


class DrumPad(object):
    INITIAL_NOTE = 36
    _FIRST_DRUM_PAD_WIDTH = 115
    _FIRST_DRUM_PAD_HEIGHT = 987

    def __init__(self, drum_pad):
        # type: (Live.DrumPad.DrumPad) -> None
        self._drum_pad = drum_pad

    def __repr__(self):
        # type: () -> str
        out = "DrumPad(name='%s', note=%s" % (self.name, self.note)
        if self.is_empty:
            out += ", empty=True"
        return out + ")"

    @property
    def name(self):
        # type: () -> str
        return smart_string(self._drum_pad.name)

    @property
    def note(self):
        # type: () -> int
        return self._drum_pad.note

    @property
    def is_empty(self):
        # type: () -> bool
        return len(self._drum_pad.chains) == 0

    @classmethod
    def select_first_pad(cls):
        # type: () -> Sequence
        Backend.client().click(cls._FIRST_DRUM_PAD_WIDTH, cls._FIRST_DRUM_PAD_HEIGHT)
        return Sequence().wait(2).done()
