from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class DummyClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(DummyClip, self).__init__(*a, **k)

        self._muted_listener.subject = self._clip

    @subject_slot("muted")
    def _muted_listener(self):
        # type: () -> None
        if self.muted:
            Backend.client().show_error("Dummy clip should not be muted")
            Scheduler.defer(partial(setattr, self, "muted", False))
