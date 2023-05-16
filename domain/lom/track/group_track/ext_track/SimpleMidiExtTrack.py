from typing import Any, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.utils.list import find_if


class SimpleMidiExtTrack(SimpleMidiTrack):
    """Tagging class for the main midi track of an ExternalSynthTrack"""

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiExtTrack, self).__init__(*a, **k)
        self.clip_tail.active = False

    @property
    def external_device(self):
        # type: () -> Optional[Device]
        return find_if(
            lambda d: d.enum is not None and d.enum.is_external_device,
            list(self.devices)
        )
