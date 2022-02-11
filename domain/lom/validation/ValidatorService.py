from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.shared.logging.Logger import Logger


class ValidatorService(object):
    def __init__(self, validator_factory):
        # type: (ValidatorFactory) -> None
        self._validator_factory = validator_factory

    def validate_object(self, obj):
        # type: (object) -> bool
        validator = self._validator_factory.create_from_object(obj)
        if validator.is_valid():
            return True
        else:
            Logger.log_warning(validator.get_error_message())
            if hasattr(obj, "color"):
                obj.color = TrackColorEnum.ERROR.color_int_value
            return False

    def fix_object(self, obj):
        # type: (object) -> None
        validator = self._validator_factory.create_from_object(obj)
        validator.fix()
        if hasattr(obj, "refresh_appearance"):
            obj.refresh_appearance()