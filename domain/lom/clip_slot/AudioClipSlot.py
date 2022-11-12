from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]
        self._clip_replaceable = False
        self._clip_loop_start = 0.0
        self._clip_loop_end = 0.0

    @subject_slot("has_clip")
    def has_clip_listener(self):
        # type: () -> None
        super(AudioClipSlot, self).has_clip_listener()

        if self.clip is not None and self._clip_replaceable:
            Logger.info("arranging replaced clip loop of %s" % self)
            Scheduler.defer(partial(self._update_clip_loop, self._clip_loop_start, self._clip_loop_end))

        self._clip_loop_start = 0
        self._clip_loop_end = 0
        self._clip_replaceable = False

    def replace_clip(self, source_clip_slot):
        # type: (AudioClipSlot) -> Optional[Sequence]
        Logger.info("Replacing %s with %s" % (self.clip, source_clip_slot.clip))

        clip_looping = self.clip.looping
        self.mark_as_replaceable()

        seq = Sequence()
        seq.add(partial(source_clip_slot.duplicate_clip_to, self))
        seq.add(lambda: setattr(self.clip, "looping", clip_looping))

        return seq.done()

    def _update_clip_loop(self, start, end):
        # type: (float, float) -> None
        self.clip.loop.start = start
        self.clip.loop.end = end

    def mark_as_replaceable(self):
        # type: () -> None
        """
            When rerecording audio, mark this audio clip slot as having its clip replaced
            it will keep its loop start and end
        """
        if self.clip is None:
            return

        self._clip_loop_start = self.clip.loop.start
        self._clip_loop_end = self.clip.loop.end
        self._clip_replaceable = True
