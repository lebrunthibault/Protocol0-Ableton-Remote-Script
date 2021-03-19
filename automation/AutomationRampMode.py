from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.lom.AbstractObject import AbstractObject


class AutomationRampMode(AbstractObject):
    __subject_events__ = ('ramp_change',)

    SCROLLING_FACTOR = 2

    def __init__(self, direction, is_active=True, exp_coeff=0, *a, **k):
        # type: (DirectionEnum, bool, float) -> None
        """ exp coeff 0 is linear, 100 is already almost a right angle """
        super(AutomationRampMode, self).__init__(*a, **k)
        self.is_active = is_active
        self.exp_coeff = float(exp_coeff)
        self.direction = direction

    def __repr__(self):
        return "direction: %s, is_active: %s, exp_coeff: %s, id: %s" % (
            self.direction, self.is_active, self.exp_coeff, id(self))

    def __str__(self):
        return "%.1f" % self.exp_coeff if self.is_active else ''

    def update_from_value(self, value=""):
        # type: (str) -> AutomationRampMode
        try:
            exp_coeff = float(value)
            self.is_active = True
            self.exp_coeff = exp_coeff
        except (ValueError, TypeError):
            self.is_active = False
            self.exp_coeff = 0

    def scroll(self, go_next):
        # type: (bool) -> None
        self.is_active = True
        factor = abs(self.exp_coeff / (10 / self.SCROLLING_FACTOR)) + 0.1
        if go_next:
            self.exp_coeff += factor
        else:
            self.exp_coeff -= factor

        # noinspection PyUnresolvedReferences
        self.notify_ramp_change()
