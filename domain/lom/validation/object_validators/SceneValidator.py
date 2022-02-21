import math

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SceneValidator(AggregateValidator):
    def __init__(self, scene):
        # type: (Scene) -> None
        validators = []
        if scene.bar_length != 0 and scene.bar_length <= 32:
            validators.append(CallbackValidator(scene, lambda s: math.log(s.bar_length, 2).is_integer(), None,
                                                "%s bar_length is not a power of 2" % scene),
                              )

        super(SceneValidator, self).__init__(validators)
