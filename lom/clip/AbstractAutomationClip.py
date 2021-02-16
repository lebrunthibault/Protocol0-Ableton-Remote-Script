from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.utils.decorators import p0_subject_slot


class AbstractAutomationClip(Clip):
    @property
    def linked_clip(self):
        # type: () -> AbstractAutomationClip
        raise NotImplementedError

    @p0_subject_slot("playing_status")
    def _playing_status_listener(self):
        if self.is_playing == self.linked_clip.is_playing:
            return

        if self.linked_clip.is_playing or self.linked_clip.is_triggered:
            self.start_marker = self.parent.utilsManager.get_next_quantized_position(self.linked_clip.playing_position, min(self.linked_clip.length, self.length))
            self.is_playing = True
        elif self.linked_clip.track.is_playing is False and self.linked_clip.track.is_triggered is False:
            self.is_playing = False
