from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface


class EmptyValidator(ValidatorInterface):
    def is_valid(self):
        # type: () -> bool
        return True

    def get_error_message(self):
        # type: () -> None
        return None

    def fix(self):
        # type: () -> None
        pass
