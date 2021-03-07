from functools import partial

from typing import TYPE_CHECKING

from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.track.group_track.AutomatedTrack import AutomatedTrack


class AutomationAudioTrack(AbstractAutomationTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.automated_parameter = None  # type: DeviceParameter
        self.abstract_group_track = self.abstract_group_track  # type: AutomatedTrack

        self._mute_listener.subject = self._track
        self._solo_listener.subject = self._track
        self._current_monitoring_state_listener.subject = self._track

        parameter_info = AbstractAutomationTrack.get_parameter_info_from_track_name(self.base_name)
        self.parent.log_debug(self.base_name)
        self.parent.log_debug(parameter_info)
        (device, parameter) = self.parent.deviceManager.get_device_and_parameter_from_name(track=self,
                                                                            device_name=parameter_info.device_name,
                                                                            parameter_name=parameter_info.parameter_name)
        self.automated_parameter = parameter
        self.has_monitor_in = True
        self.set_input_routing_type, None

        self.push2_selected_main_mode = 'device'

    @p0_subject_slot("playing_slot_index")
    def _playing_slot_index_listener(self):
        # type: () -> None
        super(AutomationAudioTrack, self)._playing_slot_index_listener()
        if self.track_name.playing_slot_index < 0:
            self.parent.defer(partial(setattr, self.automated_parameter, "value", self.automated_parameter.default_value))

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
            self.abstract_group_track.wrapped_track.set_output_routing_to(self.abstract_group_track.automation_tracks_couples[-1].audio_track)
            self.set_output_routing_to(self.next_automated_audio_track)

    @p0_subject_slot("current_monitoring_state")
    def _current_monitoring_state_listener(self):
        if not self.has_monitor_in and not any([couple.audio_track.solo for couple in self.abstract_group_track.automation_tracks_couples]):  # enforce monitor in
            self.has_monitor_in = True

        self.parent.show_message("An audio automation track should have monitor in")
