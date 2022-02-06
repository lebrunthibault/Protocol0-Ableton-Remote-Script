from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.shared.Logger import Logger


class ValidatorManager(AbstractControlSurfaceComponent):
    def validate_object(self, obj):
        # type: (object) -> bool
        validator = ValidatorFactory.create_from_object(obj)
        if validator.is_valid():
            return True
        else:
            Logger.log_warning(validator.get_error_message())
            if hasattr(obj, "color"):
                obj.color = ColorEnum.ERROR.index
            return False

    def fix_object(self, obj):
        # type: (object) -> None
        validator = ValidatorFactory.create_from_object(obj)
        validator.fix()
        if hasattr(obj, "refresh_appearance"):
            obj.refresh_appearance()
