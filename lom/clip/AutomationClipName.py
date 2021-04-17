import re

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.automation.AutomationRampMode import AutomationRampMode
from a_protocol_0.enums.DirectionEnum import DirectionEnum
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
        self._ramp_change_listener.replace_subjects(
            [
                self.automation_ramp_up,
                self.automation_ramp_down,
            ]
        )

    def __repr__(self):
        return "AutomationClipName of %s" % self.clip

    @p0_subject_slot("name")
    def _name_listener(self):
        match = re.match(
            "^(?P<base_name>[^()[\]]*)[^[\]]*(\[(?P<ramp_up>[^,]*),(?P<ramp_down>[^,]*)])?.*$", self.clip.name
        )

        self.base_name = match.group("base_name").strip() if match.group("base_name") else ""
        self.automation_ramp_up.update_from_value(match.group("ramp_up"))
        self.automation_ramp_down.update_from_value(match.group("ramp_down"))
        self.update()

    @subject_slot_group("ramp_change")
    def _ramp_change_listener(self, ramp_mode):
        self.update()

    def update(self, base_name=None, *a, **k):
        self.base_name = base_name if base_name is not None else self.base_name
        name = "%s [%s,%s]" % (self.base_name, self.automation_ramp_up, self.automation_ramp_down)
        name = name.strip()
        if "base_name" in k:
            del k["base_name"]
        super(AutomationClipName, self).update(base_name=name, *a, **k)
