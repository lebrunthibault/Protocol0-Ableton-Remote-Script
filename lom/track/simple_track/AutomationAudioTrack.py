from functools import partial

from typing import TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
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
        self.automated_device = None  # type: Device
        self.automated_parameter = None  # type: DeviceParameter
        self.linked_track = None  # type: AutomationMidiTrack
        self.abstract_group_track = self.abstract_group_track  # type: AutomatedTrack

        self._mute_listener.subject = self._track
        self._solo_listener.subject = self._track
        self._current_monitoring_state_listener.subject = self._track

        self.push2_selected_main_mode = 'device'

    def _added_track_init(self):
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")

        self.has_monitor_in = True
        seq = Sequence()
        seq.add(self.clear_devices)
        parameter_info = AbstractAutomationTrack.get_parameter_info(self.base_name)
        seq.add(partial(self.parent.browserManager.load_any_device, parameter_info.device_type, parameter_info.device_name))
        seq.add(partial(self.set_input_routing_type, None))
        seq.add(self._set_automated_device_and_parameter)

        return seq.done()

    def _on_selected(self):
        """ do specific action when track is selected """
        pass

    def _set_automated_device_and_parameter(self):
        (device, parameter) = self.get_device_and_parameter()
        self.automated_device = device
        self.automated_parameter = parameter

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
