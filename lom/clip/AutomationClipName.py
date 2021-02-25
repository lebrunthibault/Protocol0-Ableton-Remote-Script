import re

from typing import TYPE_CHECKING, Optional

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.AutomationRamp import AutomationRamp
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip


class AutomationClipName(AbstractObject):
    def __init__(self, clip, *a, **k):
        # type: (AbstractAutomationClip) -> None
        super(AutomationClipName, self).__init__(*a, **k)
        self.clip = clip
        self._base_name = ""
        self._automation_ramp_up = AutomationRamp()
        self._automation_ramp_down = AutomationRamp()
        self._name_listener.subject = self.clip._clip
        self._name_listener()

    def __repr__(self):
        return "AutomationClipName of %s" % self.clip

    @property
    def is_ramp_mode_defined(self):
        return re.match("(?P<base_name>.*)\((?P<ramps>.*)\)", self.clip.name)

    @p0_subject_slot("name")
    def _name_listener(self):
        match = re.match("(?P<base_name>[^()]*)(\((?P<ramps>.*)\))?", self.clip.name)

        self._base_name = match.group("base_name")

        if match.group("ramps") is None:
            self._automation_ramp_up = self._automation_ramp_down = AutomationRamp()
            return

        ramp_modes = match.group("ramps").split(",")
        if len(ramp_modes) > 2:
            raise Protocol0Error("You cannot define more than 2 ramp modes (up and down)")

        if len(ramp_modes) == 1:
            self._automation_ramp_up = self._automation_ramp_down = AutomationRamp.make(ramp_modes[0])
        else:
            self._automation_ramp_up = AutomationRamp.make(ramp_modes[0])
            self._automation_ramp_down = AutomationRamp.make(ramp_modes[1])

    def set(self, base_name=None, ramp_mode_up=None, ramp_mode_down=None):
        # type: (Optional[str], Optional[AutomationRamp], Optional[AutomationRamp]) -> None
        base_name = base_name or self._base_name
        ramp_mode_up = ramp_mode_up or self._automation_ramp_up
        ramp_mode_down = ramp_mode_down or self._automation_ramp_down

        self.clip.name = "%s (%s,%s)" % (base_name, ramp_mode_up, ramp_mode_down)
