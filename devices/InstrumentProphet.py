from functools import partial

from typing import Any, Optional

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractInstrument):
    NAME = "Prophet"
    TRACK_COLOR = Colors.PROPHET
    IS_EXTERNAL_SYNTH = True
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.INDEX

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentProphet, self).__init__(*a, **k)
        self.active_instance = self

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return self.active_instance != self

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        seq.add(self.device_track.select)
        seq.add(self.parent.keyboardShortcutManager.show_and_activate_rev2_editor, wait=3)
        seq.add(partial(setattr, self, "active_instance", self))

        return seq.done()
