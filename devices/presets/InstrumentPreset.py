import os

from typing import TYPE_CHECKING, Any, Optional

from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.devices.AbstractInstrument import AbstractInstrument


class InstrumentPreset(AbstractObject):
    def __init__(self, instrument, index, name, category=None, *a, **k):
        # type: (AbstractInstrument, int, Optional[str], Optional[str], Any, Any) -> None
        super(InstrumentPreset, self).__init__(*a, **k)
        self.instrument = instrument
        self.index = index
        self.original_name = name
        self.name = self._format_name(name)
        self.category = category.lower() if category else None

    def __repr__(self):
        # type: () -> str
        return "%s (%s)" % (self.name, self.index + 1)

    def _format_name(self, name):
        # type: (Optional[str]) -> str
        if not name:
            return "empty"

        base_preset_name = os.path.splitext(name)[0]  # remove file extension
        return self.instrument.format_preset_name(str(base_preset_name))  # calling subclass formatting
