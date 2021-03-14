from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractInstrument):
    NAME = "Prophet"
    TRACK_COLOR = Colors.PROPHET
    NEEDS_EXCLUSIVE_ACTIVATION = True

    def exclusive_activate(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.device_track.select)
        seq.add(self.parent.keyboardShortcutManager.show_and_activate_rev2_editor, wait=3)

        return seq.done()
