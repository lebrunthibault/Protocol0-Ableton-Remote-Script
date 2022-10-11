from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class DummyClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(DummyClip, self).__init__(*a, **k)
        # setter called from higher context
        # only way to know if the clip already has automation attached
        self.has_automation = False

    @defer
    def on_added(self):
        # type: () -> Optional[Sequence]
        # we keep existing automation when it makes sense (e.g. short loops duplicated)
        if self.has_automation and self.length < SongFacade.selected_scene().length:
            return None
        else:
            self.bar_length = SongFacade.selected_scene().bar_length

        self.clip_name.update("")
        self.muted = False

        return None
