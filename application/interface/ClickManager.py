from functools import partial

from protocol0.application.interface.PixelEnum import PixelEnum
from protocol0.domain.ApplicationView import ApplicationView
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.System import System


class ClickManager(object):
    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    def crop_clip(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(System.get_instance().right_click, 1202, 809))
        seq.add(partial(System.get_instance().click, 1262, 413))
        seq.add(wait=2)
        return seq.done()

    def save_clip_sample(self):
        # type: () -> None
        System.get_instance().click_vertical_zone(*PixelEnum.SAVE_SAMPLE.coordinates)

    def show_clip_envelope_parameter(self, clip, parameter):
        # type: (Clip, DeviceParameter) -> None
        ApplicationView.show_clip()
        clip.show_envelope()
        # noinspection PyArgumentList
        clip.view.select_envelope_parameter(parameter._device_parameter)
        if self.CLIP_ENVELOPE_SHOW_BOX_CLICKED:
            System.get_instance().double_click(*PixelEnum.SHOW_CLIP_ENVELOPE.coordinates)
            self.CLIP_ENVELOPE_SHOW_BOX_CLICKED = True
        clip.displayed_automated_parameter = parameter
