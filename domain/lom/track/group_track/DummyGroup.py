from functools import partial

from typing import Optional, Tuple, TYPE_CHECKING, Dict

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.DummyGroupValidator import (
    DummyGroupValidator,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class DummyGroup(object):
    """
    Encapsulates an optional dummy track and dummy return track
    """

    def __init__(self, track):
        # type: (AbstractGroupTrack) -> None
        self._track = track
        self._dummy_track = None  # type: Optional[SimpleDummyTrack]
        self._dummy_return_track = None  # type: Optional[SimpleDummyReturnTrack]

    def __repr__(self):
        # type: () -> str
        return "DummyGroup(dummy_track=%s, dummy_return_track=%s)" % (
            self._dummy_track,
            self._dummy_return_track,
        )

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
                    current_track = SimpleDummyTrack(detected_track._track, detected_track.index)
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
        sub_tracks = self._track.sub_tracks

        if SimpleDummyTrack.is_track_valid(sub_tracks[-1]):
            if len(sub_tracks) > 1 and SimpleDummyTrack.is_track_valid(sub_tracks[-2]):
                return sub_tracks[-2], sub_tracks[-1]
            else:
                # is it the dummy return track ?
                if SimpleDummyReturnTrack.is_track_valid(sub_tracks[-1]):
                    return None, sub_tracks[-1]
                else:
                    return sub_tracks[-1], None

        return None, None

    def fire(self, scene_index):
        # type: (int) -> None
        """
            if a dummy clip exists : fire it
            Handles gracefully automation
        """
        for dummy_track in filter(None, (self._dummy_track, self._dummy_return_track)):
            dummy_clip = dummy_track.clip_slots[scene_index].clip
            if dummy_clip is not None:
                if not self._track.is_playing:
                    # handles automation glitches on track restart
                    dummy_track.prepare_automation_for_clip_start(dummy_clip)
                dummy_clip.fire()

    def stop(self, scene_index, tails_bars_left, immediate=False, plays_on_next_scene=False):
        # type: (int, int, bool, bool) -> None
        """
            Will stop the track immediately or quantized
            the scene_index is useful for fine tuning the stop of abstract group tracks
        """
        for dummy_track in filter(None, (self._dummy_track, self._dummy_return_track)):
            dummy_clip = dummy_track.clip_slots[scene_index].clip
            if dummy_clip is None:
                continue

            dummy_clip.stop(immediate=immediate, wait_until_end=True)

            seq = Sequence()
            if not immediate and not plays_on_next_scene:
                seq.wait_bars(tails_bars_left)
            # in the (invalid) case the dummy clip is longer than the scene with tail
            seq.add(partial(dummy_clip.stop))
            if not immediate:
                seq.wait_for_event(BarChangedEvent)
            automated_parameters = dummy_clip.automation.get_automated_parameters(dummy_track.devices.parameters)
            seq.add(partial(dummy_track.reset_automated_parameters, automated_parameters))
            seq.done()

    def prepare_for_scrub(self, scene_index, clip_bar_length):
        # type: (int, float) -> None
        """
        when scrubbing playback (handling FireSceneToPositionCommand)
        the dummy clips need to be looping else it will stop on scrub_by
        and have the good length
        Only for dummy clips with tail (length % clip_length != 0)
        """
        for dummy_track in filter(None, (self._dummy_track, self._dummy_return_track)):
            dummy_clip = dummy_track.clip_slots[scene_index].clip
            if dummy_clip is not None and dummy_clip.has_tail(clip_bar_length):
                dummy_clip.set_temporary_length(clip_bar_length)

    @property
    def input_routing_track(self):
        # type: () -> SimpleTrack
        """track to route tracks to"""
        return self._dummy_track or self._track.base_track

    def get_view_track(self, scene_index):
        # type: (int) -> Optional[SimpleTrack]
        # in device view, show the dummy track only if there is a dummy clip
        if self._dummy_track is not None and self._dummy_track.clip_slots[scene_index].clip:
            return self._dummy_track
        else:
            return self._track.base_track

    def get_automated_parameters(self, scene_index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Accessible automated parameters"""
        automated_parameters = {}

        if self._dummy_track is not None:
            automated_parameters.update(self._dummy_track.get_automated_parameters(scene_index))
        if self._dummy_return_track is not None:
            automated_parameters.update(self._dummy_return_track.get_automated_parameters(scene_index))

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
        assert new_selected_parameter is not None

        return selected_track, new_selected_parameter

    def make_validator(self):
        # type: () -> ValidatorInterface
        """Keep this here allows us to prevent direct access to dummy tracks"""
        return DummyGroupValidator(self._track, self._dummy_track, self._dummy_return_track)
