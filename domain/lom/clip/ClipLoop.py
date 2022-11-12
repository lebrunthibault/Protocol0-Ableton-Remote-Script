from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

from protocol0.domain.lom.clip.ClipLoopChangedEvent import ClipLoopChangedEvent
from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class ClipLoop(SlotManager, Observable, LoopableInterface):
    """handle start / end markers and loop gracefully"""

    def __init__(self, clip):
        # type: (Live.Clip.Clip) -> None
        super(ClipLoop, self).__init__()
        self._clip = clip

        self._events_disabled = False

        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip
        self._looping_listener.subject = self._clip

        # caching this for when we set looping to False (used for tails)
        self._loop_length = None  # type: Optional[float]

    def __repr__(self):
        # type: () -> str
        return "ClipLoop(start=%s, end=%s, length=%s)" % (
            self.start,
            self.end,
            self.length,
        )

    def disable_events(self):
        # type: () -> None
        self._events_disabled = True
        Scheduler.defer(partial(setattr, self, "_events_disabled", False))

    @subject_slot("loop_start")
    def _loop_start_listener(self):
        # type: () -> None
        self._loop_listener()

    @subject_slot("loop_end")
    def _loop_end_listener(self):
        # type: () -> None
        self._loop_listener()

    @subject_slot("looping")
    def _looping_listener(self):
        # type: () -> None
        self._loop_listener()

    def _loop_listener(self):
        # type: () -> None
        if self.looping:
            self._loop_length = self.length

        self.notify_observers()
        if not self._clip.is_recording and not self._events_disabled:
            DomainEventBus.emit(ClipLoopChangedEvent(self._clip))

    @property
    def looping(self):
        # type: () -> bool
        if self._clip:
            return self._clip.looping
        else:
            return False

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        if self._clip:
            if not looping:
                self._loop_length = self.length

            self._clip.looping = looping

    @property
    def start(self):
        # type: () -> float
        if self._clip:
            return self._clip.loop_start
        else:
            return 0

    @start.setter
    def start(self, start):
        # type: (float) -> None
        looping = self.looping
        self.looping = True

        self._clip.start_marker = start
        self._clip.loop_start = start

        self.looping = looping

    @property
    def end(self):
        # type: () -> float
        if self._clip:
            return self._clip.loop_end
        else:
            return 0

    @end.setter
    def end(self, end):
        # type: (float) -> None
        looping = self.looping
        self.looping = True

        self._clip.end_marker = end
        self._clip.loop_end = end

        self.looping = looping

    @property
    def length(self):
        # type: () -> float
        """
        For looped clips: loop length in beats.
        not using unwarped audio clips
        """
        if not self._clip:
            return 0.0
        if self._clip.is_audio_clip and not self._clip.warping:
            return 0.0
        elif self._clip.length == Config.CLIP_MAX_LENGTH:  # clip is recording
            return 0.0
        else:
            return float(self._clip.length)

    @length.setter
    def length(self, length):
        # type: (float) -> None
        self.end = self.start + length

    @property
    def bar_length(self):
        # type: () -> float
        return int(self.length / SongFacade.signature_numerator())

    @bar_length.setter
    def bar_length(self, bar_length):
        # type: (float) -> None
        self.length = bar_length * SongFacade.signature_numerator()

    @property
    def loop_length(self):
        # type: () -> float
        """Return the loop length even when looping is off"""
        if self._loop_length is not None:
            return self._loop_length
        else:
            return self.length

    @property
    def full_length(self):
        # type: () -> float
        if self.length == 0:
            return 0.0
        else:
            return self._clip.end_marker - self._clip.start_marker

    @property
    def full_bar_length(self):
        # type: () -> float
        return int(self.full_length / SongFacade.signature_numerator())

    def match(self, loop):
        # type: (ClipLoop) -> None
        self.start = loop.start
        self.end = loop.end

    def fix(self):
        # type: () -> None
        self.start = self._clip.start_marker
        self.end = self._clip.end_marker
