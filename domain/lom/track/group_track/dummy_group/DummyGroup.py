from functools import partial

from typing import Optional, Tuple, TYPE_CHECKING, Dict, List

from protocol0.domain.lom.clip.DummyClip import DummyClip
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
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.shared.scheduler.Last8thPassedEvent import Last8thPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
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

    def has_automation(self, scene_index):
        # type: (int) -> bool
        return len(self._dummy_clips(scene_index)) != 0

    def fire(self, scene_index):
        # type: (int) -> None
        """
        if a dummy clip exists : fire it
        Handles gracefully automation
        """
        for dummy_track, dummy_clip in self._dummy_clips(scene_index):
            if not self._track.is_playing:
                # handles automation glitches on track restart
                dummy_track.prepare_automation_for_clip_start(dummy_clip)
            dummy_clip.fire()

    def stop(self, scene_index, next_scene_index, tail_bars_left, immediate=False):
        # type: (int, Optional[int], int, bool) -> None
        """
        Will stop the track immediately or quantized
        Stops the clip at the end of the scene or at the end of the tail clip
        """
        for dummy_track, dummy_clip in self._dummy_clips(scene_index):
            seq = Sequence()
            if not immediate:
                # in the edge case the dummy clip is set longer than the tail clip
                seq.wait_bars(min(dummy_clip.playing_position.bars_left, tail_bars_left))
            seq.add(partial(dummy_clip.stop, immediate=immediate))
            seq.done()

        self.reset_automation(scene_index, next_scene_index, tail_bars_left, immediate)

    def reset_automation(
        self, scene_index, next_scene_index=None, tails_bars_left=0, immediate=False
    ):
        # type: (int, Optional[int], int, bool) -> None
        """Reset automation when the audio tail clip (tails_bars_left) finished playing"""
        if not immediate and tails_bars_left == 0:
            seq = Sequence()
            if SongFacade.tempo() > 200:
                seq.wait_for_event(Last8thPassedEvent)
            else:
                seq.wait_for_event(Last32thPassedEvent)
            seq.add(partial(self._touch_automation, scene_index, next_scene_index))
            seq.done()

        for dummy_track, dummy_clip in self._dummy_clips(scene_index):
            Logger.dev("reset %s - %s" % (dummy_track, dummy_clip))
            seq = Sequence()
            if not immediate:
                seq.wait_bars(tails_bars_left)
                seq.wait_for_event(BarChangedEvent)
            seq.add(partial(dummy_track.reset_automated_parameters, scene_index))
            seq.done()

    def reset_all_automation(self):
        # type: () -> None
        for dummy_track in self._dummy_tracks:
            dummy_track.reset_all_automated_parameters()

    def _touch_automation(self, scene_index, next_scene_index):
        # type: (int, Optional[int]) -> None
        """
        Kinda technical : when there is a next dummy clip and it doesn't contain the automated parameter
        on the next bar, Live will set the value at the last time it was modified
        As remote script timing is not precise,
        the reset_automated_parameters stop is not instant this can create glitches
        We work around this by faking a parameter change at the bar end so that at the next bar
        Live sets this value instead, resulting in no sudden parameter value change
        """
        for dummy_track, dummy_clip in self._dummy_clips(scene_index):
            for parameter in dummy_track.get_stopping_automated_parameters(
                scene_index, next_scene_index
            ):
                envelope = dummy_clip.automation.get_envelope(parameter)
                value = envelope.value_at_time(dummy_clip.length - 0.01)
                parameter.touch(value)

    def prepare_for_scrub(self, scene_index, clip_bar_length):
        # type: (int, float) -> None
        """
        when scrubbing playback (handling FireSceneToPositionCommand)
        the dummy clips need to be looping else it will stop on scrub_by
        and have the good length
        Only for dummy clips with tail (length % clip_length != 0)
        """
        for dummy_track, dummy_clip in self._dummy_clips(scene_index):
            if dummy_clip.has_tail(clip_bar_length):
                dummy_clip.set_temporary_length(clip_bar_length)

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
        assert new_selected_parameter is not None

        return selected_track, new_selected_parameter

    def make_validator(self):
        # type: () -> ValidatorInterface
        """Keep this here allows us to prevent direct access to dummy tracks"""
        return DummyGroupValidator(self._track, self._dummy_track, self._dummy_return_track)
