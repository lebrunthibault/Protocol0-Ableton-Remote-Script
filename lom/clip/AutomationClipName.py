import re

from _Framework.SubjectSlot import subject_slot_group
from typing import TYPE_CHECKING, Optional

from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.automation.AutomationRampMode import AutomationRampMode
from a_protocol_0.lom.clip.ClipName import ClipName
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip


class AutomationClipName(ClipName):
    def __init__(self, clip, *a, **k):
        # type: (AbstractAutomationClip) -> None
        super(AutomationClipName, self).__init__(clip, *a, **k)
        self.automation_ramp_up = AutomationRampMode(direction=DirectionEnum.UP)  # type: AutomationRampMode
        self.automation_ramp_down = AutomationRampMode(direction=DirectionEnum.DOWN)  # type: AutomationRampMode
        self._ramp_change_listener.replace_subjects([
            self.automation_ramp_up,
            self.automation_ramp_down,
        ])

    def __repr__(self):
        return "AutomationClipName of %s" % self.clip

    @p0_subject_slot("name")
    def _name_listener(self):
        match = re.match("^(?P<base_name>[^()[\]]*)[^[\]]*(\[(?P<ramp_up>[^,]*),(?P<ramp_down>[^,]*)])?.*$", self.clip.name)

        self.base_name = match.group("base_name").strip() if match.group("base_name") else ""
        self.automation_ramp_up.update_from_value(match.group("ramp_up"))
        self.automation_ramp_down.update_from_value(match.group("ramp_down"))
        self.set_clip_name()

    @subject_slot_group("ramp_change")
    def _ramp_change_listener(self, ramp_mode):
        self.set_clip_name()

    def set_clip_name(self, *a, **k):
        name = self.base_name + " " if self.base_name else ""
        name = "%s[%s,%s]" % (self.base_name, self.automation_ramp_up, self.automation_ramp_down)
        super(AutomationClipName, self).set_clip_name(base_name=name, *a, **k)
