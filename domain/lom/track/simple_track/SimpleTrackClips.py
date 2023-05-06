from typing import List, TYPE_CHECKING, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.track.simple_track.SimpleTrackClipColorManager import \
    SimpleTrackClipColorManager

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots


class SimpleTrackClips(object):
    def __init__(self, clip_slots, track_devices, track_color):
        # type: (SimpleTrackClipSlots, SimpleTrackDevices, int) -> None
        self._clip_slots = clip_slots
        self.clip_color_manager = SimpleTrackClipColorManager(self, track_devices, track_color)

    def __iter__(self):
        # type: () -> Iterator[Clip]
        return iter(self._clips)

    @property
    def _clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip for clip_slot in list(self._clip_slots) if clip_slot.has_clip and clip_slot.clip
        ]
