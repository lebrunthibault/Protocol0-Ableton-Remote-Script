from functools import partial

from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import subject_slot


class AbstractAutomationClip(Clip):
    @subject_slot("playing_status")
    def _playing_status_listener(self):
        linked_clip = self._playing_status_listener.subject
        if self.is_playing == linked_clip.is_playing:
            return

        seq = Sequence()

        if linked_clip.is_playing:
            seq.add(wait=1)
            seq.add(lambda: setattr(self, "start_marker", self.parent.utilsManager.get_next_quantized_position(
                linked_clip.playing_position, linked_clip.length)))
            seq.add(lambda: setattr(self, "is_playing", True))
        # else:
        #     self.is_playing = False  " this is messed up
            # linked_clip.is_playing = False

        return seq.done()
