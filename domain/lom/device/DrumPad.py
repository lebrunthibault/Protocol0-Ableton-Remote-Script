import Live
from typing import List, cast

from _Framework.SubjectSlot import subject_slot, SlotManager
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.Sample.Sample import Sample
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.string import smart_string
from protocol0.shared.sequence.Sequence import Sequence


class DrumPad(SlotManager):
    INITIAL_NOTE = 36
    _FIRST_DRUM_PAD_WIDTH = 115
    _FIRST_DRUM_PAD_HEIGHT = 987

    def __init__(self, drum_pad):
        # type: (Live.DrumPad.DrumPad) -> None
        super(DrumPad, self).__init__()
        self._drum_pad = drum_pad
        self.chains = []  # type: List[DeviceChain]
        self._chains_listener.subject = self._drum_pad
        self._chains_listener()

    def __repr__(self):
        # type: () -> str
        out = "DrumPad(name='%s', note=%s" % (self.name, self.note)
        if self.is_empty:
            out += ", empty=True"
        return out + ")"

    @subject_slot("chains")
    def _chains_listener(self):
        # type: () -> None
        self.chains = [DeviceChain(chain, index) for index, chain in enumerate(self._drum_pad.chains)]

    @property
    def name(self):
        # type: () -> str
        return smart_string(self._drum_pad.name)

    @property
    def sample(self):
        # type: () -> Sample
        assert not self.is_empty, "pad is empty"
        simpler = cast(SimplerDevice, self.chains[0].devices[0])
        assert isinstance(simpler, SimplerDevice), "pad device is not a simpler"

        return simpler.sample

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
