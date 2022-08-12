from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import \
    PropertyValueValidator


class DummyClipValidator(AggregateValidator):
    def __init__(self, clip, devices):
        # type: (DummyClip, SimpleTrackDevices) -> None
        self._clip = clip

        validators = [
                PropertyValueValidator(clip.loop, "looping", True),
                CallbackValidator(
                    clip,
                    lambda c: len(c.automation.get_automated_parameters(devices.parameters)) > 0,
                    lambda c: c.delete(),
                    "%s has no automation" % clip,
                ),
            ]

        super(DummyClipValidator, self).__init__(validators)
