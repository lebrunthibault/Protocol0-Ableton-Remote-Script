from functools import partial

from typing import TYPE_CHECKING, Optional

from _Framework.Util import find_if
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.group_track.AutomatedTrack import AutomatedTrack


class AutomationAudioTrack(AbstractAutomationTrack):
    CLIP_CLASS = AutomationAudioClip
    CLIP_WARPING_MANDATORY = True

    def __init__(self, *a, **k):
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.automated_parameter = None  # type: Optional[DeviceParameter]
        self.abstract_group_track = self.abstract_group_track  # type: AutomatedTrack

        self._mute_listener.subject = self._track
        self._solo_listener.subject = self._track
        self._current_monitoring_state_listener.subject = self._track

        if len(self.devices) != 1:
            raise Protocol0Error("An AutomationAudioTrack should have 1 and only 1 device. For %s" % self)

        device = self.devices[0]
        self.automated_parameter = find_if(
            lambda p: self.track_name.automated_parameter_name.lower() == p.name.lower(), device.parameters
        )

        if not self.automated_parameter:
            raise Protocol0Error("Couldn't find automated parameter for %s" % self)

        self.has_monitor_in = True
        self.set_input_routing_type(None)

        self.push2_selected_main_mode = "device"

    @p0_subject_slot("playing_slot_index")
    def _playing_slot_index_listener(self):
        # type: () -> None
        """ on stopping dummy clip playing on the track, set back the automated parameter to its default value """
        super(AutomationAudioTrack, self)._playing_slot_index_listener()
        if not self.playing_clip:
            self.parent.defer(
                partial(setattr, self.automated_parameter, "value", self.automated_parameter.default_value)
            )

    @p0_subject_slot("mute")
    def _mute_listener(self):
        # mute audio effect
        if self.mute:
            self.previous_automated_audio_track.set_output_routing_to(self.next_automated_audio_track)
        else:
            self.previous_automated_audio_track.set_output_routing_to(self)

    @p0_subject_slot("solo")
    def _solo_listener(self):
        # solo audio effect
        if self.solo:
            self.abstract_group_track.wrapped_track.set_output_routing_to(self)
            self.set_output_routing_to(self.group_track)
        else:
            self.abstract_group_track.wrapped_track.set_output_routing_to(
                self.abstract_group_track.automation_tracks_couples[-1].audio_track
            )
            self.set_output_routing_to(self.next_automated_audio_track)

    @p0_subject_slot("current_monitoring_state")
    def _current_monitoring_state_listener(self):
        if not self.has_monitor_in and not any(
            couple.audio_track.toggle_solo for couple in self.abstract_group_track.automation_tracks_couples
        ):  # enforce monitor in
            self.has_monitor_in = True
