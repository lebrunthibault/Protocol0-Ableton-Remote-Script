from typing import TYPE_CHECKING

from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def select(self):
        # type: (Clip) -> None
        self.song.highlighted_clip_slot = self.clip_slot
        seq = Sequence(silent=True)
        seq.add(wait=2)
        seq.add(self.parent.clyphxNavigationManager.show_clip_view)
        return seq.done()

    def play(self):
        # type: (Clip) -> None
        if self._clip:
            self.is_playing = True

    def delete(self):
        # type: (Clip) -> None
        if not self._clip:
            return
        seq = Sequence()
        if self.is_recording:
            return
            # self.track.stop(immediate=True)

        seq.add(self.clip_slot.delete_clip, complete_on=self.clip_slot._has_clip_listener)

        if self.is_recording:
            seq.add(self.delete)

        return seq.done()

    def configure_new_clip(self):
        # type: (Clip) -> None
        """ extended """
        pass