from functools import partial

from typing import Any, Optional

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from a_protocol_0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractInstrument):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = ColorEnum.PROPHET
    IS_EXTERNAL_SYNTH = True
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.INDEX
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentProphet, self).__init__(*a, **k)

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return InstrumentProphet.ACTIVE_INSTANCE != self

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        if InstrumentProphet.ACTIVE_INSTANCE is not None:
            seq.add(self.parent.keyboardShortcutManager.show_and_activate_rev2_editor, wait=300)
        seq.add(partial(setattr, InstrumentProphet, "ACTIVE_INSTANCE", self))

        return seq.done()
