from typing import List

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SceneValidator(AggregateValidator):
    def __init__(self, scene):
        # type: (Scene) -> None
        validators = []  # type: List[ValidatorInterface]
        if scene.bar_length != 0 and scene.bar_length <= 32:
            validators.append(
                CallbackValidator(
                    scene,
                    lambda s: s.bar_length < 2 or s.bar_length % 2 == 0,
                    None,
                    "%s bar_length is not a multiple of 2" % scene,
                ),
            )

        super(SceneValidator, self).__init__(validators)
