import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Dict

from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable


class ClipLoop(SlotManager, Observable, LoopableInterface):
    """handle start / end markers and loop gracefully"""

    def __init__(self, clip):
        # type: (Live.Clip.Clip) -> None
        super(ClipLoop, self).__init__()
        self._clip = clip

        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip
        self._looping_listener.subject = self._clip

    def __repr__(self):
        # type: () -> str
        return "ClipLoop(start=%s, end=%s, length=%s)" % (
            self.start,
            self.end,
            self.length,
        )

    def to_dict(self):
        # type: () -> Dict
        return {
            "looping": self.looping,
            "start_marker": self.start_marker,
            "end_marker": self.end_marker,
            "start": self.start,
            "end": self.end,
        }

    def update_from_dict(self, loop_data):
        # type: (Dict) -> None
        self.looping = loop_data["looping"]
        self.start_marker = loop_data["start_marker"]
        self.end_marker = loop_data["end_marker"]
        self.start = loop_data["start"]
        self.end = loop_data["end"]

    @subject_slot("loop_start")
    def _loop_start_listener(self):
        # type: () -> None
        self.notify_observers()

    @subject_slot("loop_end")
    def _loop_end_listener(self):
        # type: () -> None
        self.notify_observers()

    @subject_slot("looping")
    def _looping_listener(self):
        # type: () -> None
        self.notify_observers()

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
        try:
            self._clip.loop_start = start
        except RuntimeError:
            pass

        self.looping = looping

    @property
    def start_marker(self):
        # type: () -> float
        if self._clip:
            return self._clip.start_marker
        else:
            return 0

    @start_marker.setter
    def start_marker(self, start_marker):
        # type: (float) -> None
        self._clip._start_marker = start_marker

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
        try:
            self._clip.loop_end = end
        except RuntimeError:
            pass
        self.looping = looping

    @property
    def end_marker(self):
        # type: () -> float
        if self._clip:
            return self._clip.end_marker
        else:
            return 0

    @end_marker.setter
    def end_marker(self, end_marker):
        # type: (float) -> None
        self._clip._end_marker = end_marker

    @property
    def bar_offset(self):
        # type: () -> float
        return (self.start - self.start_marker) / Song.signature_numerator()

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
        try:
            self.end = self.start + length
        except Exception as e:
            Logger.warning("clip loop length error: %s" % e)

    @property
    def bar_length(self):
        # type: () -> float
        return int(self.length / Song.signature_numerator())

    @bar_length.setter
    def bar_length(self, bar_length):
        # type: (float) -> None
        self.length = bar_length * Song.signature_numerator()

    def match(self, loop):
        # type: (ClipLoop) -> None
        self.start = loop.start
        self.end = loop.end

    def matches(self, loop):
        # type: (ClipLoop) -> bool
        return (
            self.start_marker == loop.start_marker
            and self.start == loop.start
            and self.end_marker == loop.end_marker
            and self.end == loop.end
        )

    def fix(self):
        # type: () -> None
        self.start = self.start_marker
        self.end = self.end_marker
