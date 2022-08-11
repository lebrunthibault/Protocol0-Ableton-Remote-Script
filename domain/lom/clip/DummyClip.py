from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.decorators import defer
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class DummyClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(DummyClip, self).__init__(*a, **k)
        self._muted_listener.subject = self._clip
        # setter called from higher context
        # only way to know if the clip already has automation attached
        self.has_automation = False

    @defer
    def on_added(self):
        # type: () -> Optional[Sequence]
        # we keep existing automation when it makes sense (e.g. short loops duplicated)
        if self.has_automation and self.loop.length < SongFacade.selected_scene().length:
            return None
        else:
            self.loop.bar_length = SongFacade.selected_scene().bar_length

        self.clip_name.update("")

        return None

    @subject_slot("muted")
    def _muted_listener(self):
        # type: () -> None
        if self.muted:
            Logger.warning("Dummy clip should not be muted")
            Scheduler.defer(partial(setattr, self, "muted", False))
