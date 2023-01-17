from typing import Optional, Tuple, TYPE_CHECKING, Dict, List

from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.DummyGroupValidator import (
    DummyGroupValidator,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class DummyGroup(object):
    """
    Encapsulates an optional dummy track and dummy return track
    """

    def __init__(self, track, is_active=True):
        # type: (AbstractGroupTrack, bool) -> None
        self._track = track
        self._dummy_track = None  # type: Optional[SimpleDummyTrack]
        self._dummy_return_track = None  # type: Optional[SimpleDummyReturnTrack]
        self._is_active = is_active

    def __repr__(self):
        # type: () -> str
        return "DummyGroup(dummy_track=%s, dummy_return_track=%s)" % (
            self._dummy_track,
            self._dummy_return_track,
        )

    @property
    def _dummy_tracks(self):
        # type: () -> List[SimpleDummyTrack]
        return list(filter(None, (self._dummy_track, self._dummy_return_track)))

    def _dummy_clips(self, scene_index):
        # type: (int) -> List[Tuple[SimpleDummyTrack, DummyClip]]
        clips = []
        for track in self._dummy_tracks:
            clip = track.clip_slots[scene_index].clip
            if clip is not None:
                clips.append((track, clip))

        return clips

    @property
    def devices(self):
        # type: () -> List[Device]
        if self._dummy_track is not None:
            return self._dummy_track.devices
        else:
            return []

    def map_tracks(self):
        # type: () -> None
        dummy_track, dummy_return_track = self._get_tracks()

        # no change
        if dummy_track == self._dummy_track and dummy_return_track == self._dummy_return_track:
            return None

        for track_prop, detected_track, cls in (
            ("_dummy_track", dummy_track, SimpleDummyTrack),
            ("_dummy_return_track", dummy_return_track, SimpleDummyReturnTrack),
        ):
            current_track = getattr(self, track_prop)
            if detected_track is not None:
                if detected_track._track != getattr(current_track, "_track", None):
                    current_track = cls(detected_track._track, detected_track.index)
                    setattr(self, track_prop, current_track)
                    self._track.add_or_replace_sub_track(current_track, detected_track)
                    self._track.link_sub_track(current_track)
            else:
                setattr(self, track_prop, None)
                if current_track is not None:
                    current_track.disconnect()

        Scheduler.wait(3, self._track.route_sub_tracks)

    def _get_tracks(self):
        # type: () -> Tuple[Optional[AbstractTrack], Optional[AbstractTrack]]
        if not self._is_active:
            return None, None

        sub_tracks = self._track.sub_tracks

        has_foldable_sub_track = any(sub_track.base_track.is_foldable for sub_track in sub_tracks)
        # when finding only SimpleTracks we don't activate dummy tracks
        if len(sub_tracks) < 2 or not has_foldable_sub_track:
            return None, None

        if SimpleDummyTrack.is_track_valid(sub_tracks[-1]):
            return sub_tracks[-1], None
        elif SimpleDummyTrack.is_track_valid(
            sub_tracks[-2]
        ) and SimpleDummyReturnTrack.is_track_valid(sub_tracks[-1]):
            return sub_tracks[-2], sub_tracks[-1]
        else:
            return None, None

    def has_automation(self, scene_index):
        # type: (int) -> bool
        return len(self._dummy_clips(scene_index)) != 0

    def solo(self):
        # type: () -> None
        if self._dummy_return_track is not None:
            self._dummy_return_track.solo = True

    def reset_all_automation(self):
        # type: () -> None
        for dummy_track in self._dummy_tracks:
            dummy_track.reset_all_automated_parameters()

    @property
    def input_routing_track(self):
        # type: () -> SimpleTrack
        """track to route tracks to"""
        return self._dummy_track or self._track.base_track

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        # in device view, show the dummy track only if there is a dummy clip
        if (
            self._dummy_track is not None
            and self._dummy_track.clip_slots[scene_index].clip is not None
        ):
            return self._dummy_track
        else:
            return self._track.base_track

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Accessible automated parameters"""
        automated_parameters = {}

        for dummy_track in self._dummy_tracks:
            automated_parameters.update(dummy_track.get_automated_parameters(scene_index))

        return automated_parameters

    def get_selected_mixer_parameter(self, selected_parameter):
        # type: (DeviceParameter) -> Tuple[SimpleDummyReturnTrack, DeviceParameter]
        if self._dummy_return_track is None:
            raise Protocol0Warning("Send parameters need a dummy return track")

        selected_track = self._dummy_return_track
        new_selected_parameter = find_if(
            lambda p: p.is_mixer_parameter and p.name == selected_parameter.name,
            self._dummy_return_track.devices.parameters,
        )
        assert new_selected_parameter is not None, "Cannot find selected mixer parameter"

        return selected_track, new_selected_parameter

    def make_validator(self):
        # type: () -> ValidatorInterface
        """Keep this here allows us to prevent direct access to dummy tracks"""
        return DummyGroupValidator(self._track, self._dummy_track, self._dummy_return_track)
