from typing import TYPE_CHECKING, Optional

from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def select(self):
        # type: (Clip) -> Sequence
        self.song.highlighted_clip_slot = self.clip_slot
        seq = Sequence(silent=True)
        seq.add(wait=10)
        seq.add(self.parent.clyphxNavigationManager.show_clip_view)
        return seq.done()

    def play(self):
        # type: (Clip) -> None
        self.is_playing = True

    def play_stop(self):
        # type: (Clip) -> None
        self.is_playing = not self.is_playing

    @defer
    def delete(self):
        # type: (Clip) -> Optional[Sequence]
        if not self._clip:
            return None
        seq = Sequence()
        seq.add(self.clip_slot.delete_clip, complete_on=self.clip_slot._has_clip_listener)
        return seq.done()

    def configure_new_clip(self):
        # type: (Clip) -> None
        """ extended """
        pass
