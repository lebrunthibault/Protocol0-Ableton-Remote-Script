from a_protocol_0.lom.clip.AutomationClipName import AutomationClipName
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.utils.decorators import p0_subject_slot


class AbstractAutomationClip(Clip):
    def __init__(self, *a, **k):
        super(AbstractAutomationClip, self).__init__(*a, **k)
        self.clip_name = AutomationClipName(self)

    @property
    def automation_ramp_up(self):
        return self.clip_name._automation_ramp_up

    @property
    def automation_ramp_down(self):
        return self.clip_name._automation_ramp_down

    @property
    def linked_clip(self):
        # type: () -> AbstractAutomationClip
        raise NotImplementedError

    @p0_subject_slot("playing_status")
    def _playing_status_linked_clip_listener(self):
        if self.is_playing == self.linked_clip.is_playing:
            return

        if self.linked_clip.is_playing or self.linked_clip.is_triggered:
            # self.start_marker = self.parent.utilsManager.get_next_quantized_position(self.linked_clip.playing_position, min(self.linked_clip.length, self.length))
            self.is_playing = True
        elif self.linked_clip.clip.is_playing is False and self.linked_clip.clip.is_triggered is False:
            self.is_playing = False

    @p0_subject_slot("is_triggered")
    def _is_triggered_linked_clip_listener(self):
        if self.is_triggered == self.linked_clip.is_triggered:
            return

        if self.linked_clip.is_triggered:
            # self.start_marker = self.parent.utilsManager.get_next_quantized_position(self.linked_clip.playing_position, min(self.linked_clip.length, self.length))
            self.is_playing = True
        else:
            self.is_playing = False
