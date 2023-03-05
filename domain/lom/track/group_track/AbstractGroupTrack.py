from typing import List, Optional, Dict

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.group_track.dummy_group.DummyGroup import DummyGroup
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(base_group_track)
        self.base_track.abstract_group_track = self
        # filled when link_sub_tracks is called
        self.group_track = self.group_track  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves on_tracks_change
        self.dummy_group = DummyGroup(self, is_active=False)

        self.appearance.register_observer(self)

    def on_tracks_change(self):
        # type: () -> None
        # 2nd layer linking : here we don't necessarily link the sub tracks to self
        self.sub_tracks[:] = self.base_track.sub_tracks
        self._link_group_track()
        self.dummy_group.map_tracks()

    def link_sub_track(self, sub_track):
        # type: (SimpleTrack) -> None
        sub_track.group_track = self.base_track
        sub_track.abstract_group_track = self

    def _link_group_track(self):
        # type: () -> None
        """2nd layer linking : Connect to the enclosing abg group track is any"""
        if self.base_track.group_track is None:
            self.group_track = None
            return

        # NB : self.group_track is necessarily not None here because a foldable track always has an abg
        self.group_track = self.base_track.group_track.abstract_group_track
        self.abstract_group_track = self  # because we already are the abstract group track
        self.group_track.add_or_replace_sub_track(self, self.base_track)

    def get_all_simple_sub_tracks(self):
        # type: () -> List[SimpleTrack]
        sub_tracks = []
        for sub_track in self.sub_tracks:
            if isinstance(sub_track, AbstractGroupTrack):
                sub_tracks += sub_track.get_all_simple_sub_tracks()
            else:
                sub_tracks.append(sub_track)

        return sub_tracks  # noqa

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        """track to show when scrolling scene tracks"""
        if ApplicationView.is_clip_view_visible():
            return None
        else:
            return self.dummy_group.get_view_track(scene_index)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackAppearance):
            for sub_track in self.sub_tracks:
                sub_track.color = self.appearance.color

    def clear_clips(self):
        # type: () -> Sequence
        return Sequence().add([t.clear_clips for t in self.sub_tracks]).done()

    @property
    def color(self):
        # type: () -> int
        return self.base_track.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.base_track.color = color_index
        for track in self.sub_tracks:
            track.color = color_index

    def fire(self, scene_index):
        # type: (int) -> None
        for track in self.sub_tracks:
            track.fire(scene_index)

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        for track in self.sub_tracks:
            track.stop(scene_index, next_scene_index, immediate)

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Accessible automated parameters"""
        result = {}
        for track in self.sub_tracks:
            result.update(track.get_automated_parameters(scene_index))

        return result
