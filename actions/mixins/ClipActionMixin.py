from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def action_delete(self):
        # type: ("Clip") -> None
        self.clip_slot.delete_clip()
        if self.is_recording:
            qz = self.track.song.clip_trigger_quantization
            self.track.song.clip_trigger_quantization = 0
            self.track.stop()

            def delete_recording_clip():
                self.action_delete()
                self.track.song.clip_trigger_quantization = qz

            self.track.parent.wait(2, delete_recording_clip)
