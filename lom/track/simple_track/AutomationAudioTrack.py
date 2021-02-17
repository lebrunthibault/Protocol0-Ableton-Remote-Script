from functools import partial

from typing import List, TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationAudioTrack(AbstractAutomationTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.clip_slots = self.clip_slots  # type: List[AutomationAudioClipSlot]
        self.automated_device = None  # type: Device
        self.automated_parameter = None  # type: DeviceParameter
        self._current_monitoring_state_listener.subject = self._track
        self.automated_midi_track = None  # type: AutomationMidiTrack
        self.push2_selected_main_mode = 'device'

    def _connect(self, track):
        # type: (AutomationMidiTrack) -> None
        self.automated_midi_track = track

    def _added_track_init(self):
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")

        self.has_monitor_in = True
        seq = Sequence()
        seq.add(self.clear_devices)
        seq.add(partial(self.parent.browserManager.load_rack_device, self.base_name.split(":")[1]))
        seq.add(partial(self.set_input_routing_type, None))
        seq.add(self._get_automated_device_and_parameter)

        return seq.done()

    def _on_selected(self):
        """ do specific action when track is selected """
        pass

    def _get_automated_device_and_parameter(self):
        [_, device_name, parameter_name] = self.base_name.split(":")
        (device, parameter) = self.parent.deviceManager.get_device_and_parameter_from_name(track=self, device_name=device_name, parameter_name=parameter_name)
        self.automated_device = device
        self.automated_parameter = parameter

    @p0_subject_slot("current_monitoring_state")
    def _current_monitoring_state_listener(self):
        if not self.has_monitor_in:
            self.has_monitor_in = True

        self.parent.show_message("An audio automation track should have monitor in")
