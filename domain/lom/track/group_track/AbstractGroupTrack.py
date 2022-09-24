from _Framework.SubjectSlot import subject_slot
from typing import List, Optional, Dict

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.group_track.dummy_group.DummyGroup import DummyGroup
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(base_group_track)
        self.base_track.abstract_group_track = self
        # filled when link_sub_tracks is called
        self.group_track = self.group_track  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves on_tracks_change
        self.dummy_group = DummyGroup(self)

        self._solo_listener.subject = self._track

        self.appearance.register_observer(self)
        self._force_clip_colors = True

    def on_tracks_change(self):
        # type: () -> None
        self._link_sub_tracks()
        self._link_group_track()
        self.dummy_group.map_tracks()

    def _link_sub_tracks(self):
        # type: () -> None
        """2nd layer linking"""
        # here we don't necessarily link the sub tracks to self
        self.sub_tracks[:] = self.base_track.sub_tracks

    def link_sub_track(self, sub_track):
        # type: (SimpleTrack) -> None
        sub_track.group_track = self.base_track
        sub_track.abstract_group_track = self

    def _link_group_track(self):
        # type: () -> None
        """
        2nd layer linking
        Connect to the enclosing abg group track is any
        """
        if self.base_track.group_track is None:
            self.group_track = None
            return

        # NB : self.group_track is necessarily not None here because a foldable track always has an abg
        assert self.base_track.group_track.abstract_group_track
        self.group_track = self.base_track.group_track.abstract_group_track
        self.abstract_group_track = self  # because we already are the abstract group track
        self.group_track.add_or_replace_sub_track(self, self.base_track)

    def route_sub_tracks(self):
        # type: () -> None
        for sub_track in self.sub_tracks:
            if not isinstance(sub_track, SimpleDummyTrack):
                sub_track.output_routing.track = self.dummy_group.input_routing_track

    def is_parent(self, abstract_track):
        # type: (AbstractTrack) -> bool
        """checks if the given track is not itself or a possibly nested child"""
        return (
            abstract_track == self
            or abstract_track in self.sub_tracks
            or any(
                isinstance(sub_track, AbstractGroupTrack) and sub_track.is_parent(abstract_track)
                for sub_track in self.sub_tracks
            )
        )

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        """track to show when scrolling scene tracks"""
        if ApplicationViewFacade.is_clip_view_visible():
            return None
        else:
            return self.dummy_group.get_view_track(scene_index)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackAppearance):
            for sub_track in self.sub_tracks:
                sub_track.appearance.color = self.appearance.color
                # this is when moving tracks into a different group
                if self._force_clip_colors:
                    for clip in sub_track.clips:
                        clip.color = self.appearance.color

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self.base_track.clip_slots

    @subject_slot("solo")
    @defer
    def _solo_listener(self):
        # type: () -> None
        if self.solo:
            self.dummy_group.solo()

            for sub_track in self.sub_tracks:
                sub_track.solo = True

    def bars_left(self, scene_index):
        # type: (int) -> int
        """Returns the truncated number of bars left before the track stops on this particular scene"""
        return max([sub_track.bars_left(scene_index) for sub_track in self.sub_tracks] or [0])

    def fire(self, scene_index):
        # type: (int) -> None
        super(AbstractGroupTrack, self).fire(scene_index)

        self.dummy_group.fire(scene_index)

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        """
        Will stop the track immediately or quantized
        the scene_index is useful for fine tuning the stop of abstract group tracks
        """
        super(AbstractGroupTrack, self).stop(scene_index, immediate=immediate)

        if scene_index is not None:
            bars_left = self.bars_left(scene_index)
            if next_scene_index is not None:
                next_scene = SongFacade.scenes()[next_scene_index]
                # checks that the track or any of its sub tracks plays on next scene or that
                # the sub track check is here to handle dummy clip termination
                if next_scene and any(self.contains_track(t) for t in next_scene.abstract_tracks):
                    bars_left = 0
            self.dummy_group.stop(scene_index, next_scene_index, bars_left, immediate)

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Accessible automated parameters"""
        return self.dummy_group.get_automated_parameters(scene_index)
