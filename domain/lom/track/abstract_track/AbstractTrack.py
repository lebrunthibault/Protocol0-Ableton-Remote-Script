import Live
from _Framework.SubjectSlot import SlotManager
from typing import Optional, List, cast, TYPE_CHECKING, Dict

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.TrackDisconnectedEvent import TrackDisconnectedEvent
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import (
    AbstractTrackSelectedEvent,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(SlotManager):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(AbstractTrack, self).__init__()
        # TRACKS
        self._track = track._track  # type: Live.Track.Track
        self.base_track = track  # type: SimpleTrack
        self.group_track = None  # type: Optional[AbstractTrack]
        # NB : .group_track is simple for simple tracks and abg for abg tracks
        self.abstract_group_track = None  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]

        # MISC
        self.arm_state = AbstractTrackArmState(self._track)  # type: AbstractTrackArmState
        self.appearance = AbstractTrackAppearance(self._track)

    def __repr__(self):
        # type: () -> str
        return "%s : %s (%s)" % (self.__class__.__name__, self._track.name, self.index + 1)

    def on_added(self):
        # type: () -> Optional[Sequence]
        if self.group_track is not None:
            if self.group_track.color != self.color:
                self.color = self.group_track.color

        return None

    def on_tracks_change(self):
        # type: () -> None
        raise NotImplementedError

    def on_scenes_change(self):
        # type: () -> None
        pass

    @property
    def index(self):
        # type: () -> int
        return self.base_track._index

    @property
    def abstract_track(self):
        # type: () -> AbstractTrack
        """
        For top level SimpleTracks, will return self
        For AbstractGroupTracks, will return self (NormalGroupTrack and ExternalSynthTrack)
        Only for nested SimpleTracks, will return their abstract_group_track
        """
        if self.abstract_group_track:
            return self.abstract_group_track
        else:
            return self

    @property
    def group_tracks(self):
        # type: () -> List[AbstractGroupTrack]
        if not self.group_track:
            return []
        return [self.group_track.abstract_track] + self.group_track.group_tracks

    def add_or_replace_sub_track(self, sub_track, previous_sub_track=None):
        # type: (AbstractTrack, Optional[AbstractTrack]) -> None
        if sub_track in self.sub_tracks:
            return

        if sub_track._track == self._track:  # same track
            return

        if previous_sub_track is None or previous_sub_track not in self.sub_tracks:
            self.sub_tracks.append(sub_track)
        else:
            sub_track_index = self.sub_tracks.index(previous_sub_track)
            self.sub_tracks[sub_track_index] = sub_track

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        """Depending on the current view returns the appropriate track"""
        return self.base_track

    @property
    def instrument(self):
        # type: () -> Optional[InstrumentInterface]
        return None

    name = cast(str, ForwardTo("appearance", "name"))

    @property
    def color(self):
        # type: () -> int
        raise NotImplementedError

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        raise NotImplementedError

    @property
    def solo(self):
        # type: () -> bool
        return self._track and self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        if self._track:
            self._track.solo = solo

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track and self._track.is_visible

    @property
    def muted(self):
        # type: () -> bool
        return self._track and self._track.mute

    @muted.setter
    def muted(self, mute):
        # type: (bool) -> None
        if self._track:
            self._track.mute = mute

    def select(self):
        # type: () -> None
        DomainEventBus.emit(AbstractTrackSelectedEvent(self._track))

    def fire(self, scene_index):
        # type: (int) -> None
        raise NotImplementedError

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        raise NotImplementedError

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Due to AbstractGroupTrack we cannot do this only at clip level"""
        raise NotImplementedError

    @property
    def load_time(self):
        # type: () -> int
        raise NotImplementedError

    def to_dict(self):
        # type: () -> Dict
        return {"name": self.name, "type": self.__class__.__name__, "index": self.index}

    def disconnect(self):
        # type: () -> None
        super(AbstractTrack, self).disconnect()
        self.appearance.disconnect()
        DomainEventBus.emit(TrackDisconnectedEvent(self))
