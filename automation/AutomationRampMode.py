from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.lom.AbstractObject import AbstractObject


class AutomationRampMode(AbstractObject):
    __subject_events__ = ("ramp_change",)

    SCROLLING_FACTOR = 2

    def __init__(self, direction, is_active=True, exp_coeff=0, *a, **k):
        # type: (DirectionEnum, bool, float) -> None
        """ exp coeff 0 is linear, 100 is already almost a right angle """
        super(AutomationRampMode, self).__init__(*a, **k)
        self._is_active = is_active
        self._exp_coeff = float(exp_coeff)
        self.direction = direction

    def __repr__(self):
        return "direction: %s, is_active: %s, exp_coeff: %s, id: %s" % (
            self.direction,
            self.is_active,
            self.exp_coeff,
            id(self),
        )

    def __str__(self):
        return "%.1f" % self.exp_coeff if self.is_active else ""

    def update_from_value(self, value=""):
        # type: (str) -> AutomationRampMode
        try:
            exp_coeff = float(value)
            self.is_active = True
            self.exp_coeff = exp_coeff
        except (ValueError, TypeError):
            self.is_active = False
            self.exp_coeff = 0

    @property
    def is_active(self):
        # type: () -> bool
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        # type: (bool) -> None
        if is_active != self._is_active:
            self._is_active = is_active
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.notify_ramp_change)

    @property
    def exp_coeff(self):
        # type: () -> float
        return self._exp_coeff

    @exp_coeff.setter
    def exp_coeff(self, exp_coeff):
        # type: (float) -> None
        if exp_coeff != self._exp_coeff:
            self._exp_coeff = exp_coeff
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.notify_ramp_change)

    def scroll(self, go_next):
        # type: (bool) -> None
        self.is_active = True
        factor = abs(self.exp_coeff / (10 / self.SCROLLING_FACTOR)) + 0.1
        if go_next:
            self.exp_coeff += factor
        else:
            self.exp_coeff -= factor
