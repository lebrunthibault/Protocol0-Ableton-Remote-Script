from typing import Any

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from a_protocol_0.lom.AbstractObject import AbstractObject


class AbstractControlSurfaceComponent(AbstractObject, ControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        AbstractObject.__init__(self, *a, **k)
        ControlSurfaceComponent.__init__(self, song=self.parent.protocol0_song, *a, **k)

