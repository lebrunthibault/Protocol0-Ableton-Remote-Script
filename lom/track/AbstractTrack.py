from abc import abstractproperty
from typing import Any, Optional, List
from typing import TYPE_CHECKING

import Live

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import TRACK_CATEGORIES, TRACK_CATEGORY_OTHER
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.utils.utils import find_all_devices

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, AbstractControlSurfaceComponent):
    def __init__(self, track, index, *a, **k):
        # type: (Live.Track.Track, int, Any, Any) -> None
        self._track = track  # type: Live.Track.Track
        self._view = track.view  # type: Live.Track.Track.View
        super(AbstractTrack, self).__init__(name=self.name, *a, **k)
        self.index = index
        self.base_track = self  # type: SimpleTrack
        self.selectable_track = self
        self.group_track = None  # type: Optional[SimpleTrack]
        self.group_tracks = []  # type: List[SimpleTrack]
        self.sub_tracks = []  # type: List[SimpleTrack]
        self.top_devices = self._track.devices  # type: List[Live.Device.Device]
        self.all_devices = find_all_devices(self._track)  # type: List[Live.Device.Device]
        self.instrument = self.parent.deviceManager.create_instrument_from_simple_track(track=self)
        self.is_foldable = self._track.is_foldable
        self.can_be_armed = self._track.can_be_armed
        self.selected_recording_time = "1 bar"
        self.bar_count = 1
        self.base_color = getattr(Colors, self.name) if Colors.has(self.name) else self._track.color_index  # type: int

    @property
    def all_tracks(self):
        # type: () -> List[SimpleTrack]
        all_tracks = [self]
        [all_tracks.extend(sub_track.all_tracks) for sub_track in self.sub_tracks]
        return all_tracks

    @property
    def selected_device(self):
        # type: () -> Live.Device.Device
        return self._track.view.selected_device

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def name(self):
        # type: () -> str
        return self._track.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self._track.name = name

    @property
    def category(self):
        # type: () -> str
        for track_category in TRACK_CATEGORIES:
            if any([t for t in [self] + self.group_tracks if t.name.lower() == track_category.lower()]):
                return track_category

        return TRACK_CATEGORY_OTHER

    @property
    def color(self):
        # type: () -> int
        return self._track.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        for track in self.all_tracks:
            track._track.color_index = color_index

    @property
    def is_folded(self):
        # type: () -> bool
        return self._track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self._track.fold_state = int(is_folded)

    @abstractproperty
    def is_playing(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_recording(self):
        # type: () -> bool
        pass

    @abstractproperty
    def arm(self):
        # type: () -> bool
        pass
