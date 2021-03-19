from a_protocol_0.lom.clip.AutomationClipName import AutomationClipName
from a_protocol_0.lom.clip.Clip import Clip


class AbstractAutomationClip(Clip):
    def __init__(self, *a, **k):
        super(AbstractAutomationClip, self).__init__(set_clip_name=False, *a, **k)
        # handled by the ClipSynchronizer
        self.clip_name = None  # type: AutomationClipName

    @property
    def automation_ramp_up(self):
        return self.clip_name.automation_ramp_up

    @property
    def automation_ramp_down(self):
        return self.clip_name.automation_ramp_down
