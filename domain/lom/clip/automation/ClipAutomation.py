import Live
from typing import Optional, List, cast

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.automation.ClipAutomationEnvelope import ClipAutomationEnvelope
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.errors.error_handler import handle_error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ClipAutomation(object):
    def __init__(self, live_clip, loop):
        # type: (Live.Clip.Clip, ClipLoop) -> None
        self._live_clip = live_clip
        self._loop = loop

    def get_hash(self, device_parameters):
        # type: (List[DeviceParameter]) -> int
        automated_parameters = self.get_automated_parameters(device_parameters)
        envs = [self.get_envelope(param) for param in automated_parameters]

        return hash(tuple([env.hash for env in envs]))

    def has_automation(self, device_parameters):
        # type: (List[DeviceParameter]) -> bool
        return len(self.get_automated_parameters(device_parameters)) != 0

    def get_automated_parameters(self, device_parameters):
        # type: (List[DeviceParameter]) -> List[DeviceParameter]
        automated_parameters = []
        for parameter in device_parameters:
            # ignore rev2 b layer (we edit only A)
            if parameter.name.startswith("B-"):
                continue
            if self.get_envelope(parameter) is None:
                continue

            automated_parameters.append(parameter)

        return automated_parameters

    def show_parameter_envelope(self, parameter):
        # type: (DeviceParameter) -> None
        ApplicationView.show_clip()
        self.show_envelope()
        # noinspection PyArgumentList
        self._live_clip.view.select_envelope_parameter(parameter._device_parameter)
        DomainEventBus.emit(ClipEnvelopeShowedEvent())

    def get_envelope(self, parameter):
        # type: (DeviceParameter) -> Optional[ClipAutomationEnvelope]
        if self._live_clip and parameter._device_parameter:
            env = self._live_clip.automation_envelope(parameter._device_parameter)
            if env:
                return ClipAutomationEnvelope(env, self._loop.length)

        return None

    def select_or_create_envelope(self, parameter):
        # type: (DeviceParameter) -> None
        envelope = self.get_envelope(parameter)
        if envelope is None:
            envelope = self.create_envelope(parameter)

        envelope.create_start_and_end_points()

        self.show_parameter_envelope(parameter)

    def create_envelope(self, parameter):
        # type: (DeviceParameter) -> ClipAutomationEnvelope
        try:
            self._live_clip.create_automation_envelope(parameter._device_parameter)
        except RuntimeError:
            # envelope already exists
            pass
        return cast(ClipAutomationEnvelope, self.get_envelope(parameter))

    def clear_all_envelopes(self):
        # type: () -> None
        if self._live_clip:
            return self._live_clip.clear_all_envelopes()

    @handle_error
    def show_envelope(self):
        # type: () -> None
        self.hide_envelope()  # necessary
        self._live_clip.view.show_loop()  # this before seem to work better
        self._live_clip.view.show_envelope()

    @handle_error
    def hide_envelope(self):
        # type: () -> None
        self._live_clip.view.hide_envelope()
