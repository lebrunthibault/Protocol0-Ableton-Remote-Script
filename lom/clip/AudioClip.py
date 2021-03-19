import Live

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.utils.decorators import is_change_deferrable, p0_subject_slot


class AudioClip(Clip):
    def __init__(self, *a, **k):
        super(AudioClip, self).__init__(*a, **k)
        self._warping_listener.subject = self._clip

    @p0_subject_slot("warping")
    def _warping_listener(self):
        if self.warping:
            self.looping = True

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    @is_change_deferrable
    def warping(self, warping):
        # type: (float) -> None
        if self._clip:
            self._clip.warping = warping

    @property
    def warp_mode(self):
        return self._clip.warp_mode

    @warp_mode.setter
    @is_change_deferrable
    def warp_mode(self, warp_mode):
        if self._clip:
            self._clip.warp_mode = warp_mode

    def automation_envelope(self, parameter):
        # type: (DeviceParameter) -> Live.Clip.AutomationEnvelope
        return self._clip and self._clip.automation_envelope(parameter._device_parameter)

    def create_automation_envelope(self, parameter):
        # type: (Clip, DeviceParameter) -> Live.Clip.AutomationEnvelope
        if parameter is None:
            raise Protocol0Error("You passed None to Clip.create_automation_envelope for clip %s" % self)
        return self._clip.create_automation_envelope(parameter._device_parameter)

    def clear_all_envelopes(self):
        # type: (Clip) -> None
        if self._clip:
            return self._clip.clear_all_envelopes()
