from functools import partial

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractInstrument):
    NEEDS_EXCLUSIVE_ACTIVATION = True

    def exclusive_activate(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(self.song.select_track, self.device_track))
        seq.add(self.parent.keyboardShortcutManager.show_and_activate_rev2_editor, wait=3)

        return seq.done()
