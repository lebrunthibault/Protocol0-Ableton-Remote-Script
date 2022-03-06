from functools import partial

from typing import TYPE_CHECKING

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.MidiClip import MidiClip


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

    def link_clip_automation(self, clip):
        # type: (MidiClip) -> Sequence
        a_env = clip.automation_envelope(self._param_a)
        b_env = clip.automation_envelope(self._param_b)

        seq = Sequence()
        seq.add(partial(clip.show_parameter_envelope, self._param_a))
        seq.add(a_env.focus)
        seq.wait(3)
        seq.add(a_env.copy)
        seq.wait(10)
        seq.add(partial(clip.show_parameter_envelope, self._param_b))
        seq.add(b_env.paste)
        seq.wait(10)
        return seq.done()
