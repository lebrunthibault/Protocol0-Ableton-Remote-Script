from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.validation.ValidatorFactory import ValidatorFactory


class ValidatorManager(AbstractControlSurfaceComponent):
    def validate_object(self, obj):
        # type: (AbstractObject) -> bool
        validator = ValidatorFactory.create_from_object(obj)
        if validator.is_valid():
            return True
        else:
            self.parent.log_warning(validator.get_error_message())
            if hasattr(obj, "color"):
                obj.color = ColorEnum.ERROR.index
            return False

    def fix_object(self, obj):
        # type: (AbstractObject) -> None
        validator = ValidatorFactory.create_from_object(obj)
        validator.fix()
        obj.refresh_appearance()
