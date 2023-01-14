from functools import partial

from protocol0.domain.lom.clip.automation.ClipAutomation import ClipAutomation
from protocol0.domain.lom.clip.automation.ClipAutomationEnvelope import ClipAutomationEnvelope
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.sequence.Sequence import Sequence


class LinkedDeviceParameters(object):
    """
    NB : targeted at my rev2 as it has two identical layers
    and we cannot edit multiple automation curves at the same time
    """

    def __init__(self, param_a, param_b):
        # type: (DeviceParameter, DeviceParameter) -> None
        self._param_a = param_a
        self._param_b = param_b

    def __repr__(self):
        # type: () -> str
        return "(param_a: %s, param_b: %s)" % (self._param_a, self._param_b)

    def link_clip_automation(self, automation):
        # type: (ClipAutomation) -> Sequence
        a_env = automation.get_envelope(self._param_a)
        b_env = automation.get_envelope(self._param_b)

        seq = Sequence()
        seq.add(partial(automation.show_parameter_envelope, self._param_a))
        seq.add(ClipAutomationEnvelope.focus)
        seq.wait(3)
        seq.add(a_env.copy)
        seq.wait(10)
        seq.add(partial(automation.show_parameter_envelope, self._param_b))
        seq.add(b_env.paste)
        seq.wait(10)
        return seq.done()
