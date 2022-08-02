from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Any

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        self._warping_listener.subject = self._clip
        Scheduler.defer(self.appearance.refresh)

    @subject_slot("warping")
    def _warping_listener(self):
        # type: () -> None
        if self._clip.warping:
            Scheduler.defer(partial(setattr, self, "looping", True))
        self.notify_observers()

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    def crop(self):
        # type: () -> None
        """Live.Clip.Clip.crop_sample doesn't exist, so we notify the user"""
        self.appearance.color = ColorEnum.WARNING.color_int_value
        Logger.warning("Please crop %s" % self)

    def play_and_mute(self):
        # type: () -> Sequence
        self.muted = False
        seq = Sequence()

        seq.defer()  # wait for unmute
        seq.log("play and mute")
        seq.add(self.fire)
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)  # wait for the clip
        # start
        seq.wait_bars(self.loop.bar_length)
        seq.wait(5)
        # seq.add(self._mute_if_stopped)

        return seq.done()

    def _mute_if_stopped(self):
        # type: () -> None
        if not self.is_playing:
            self.muted = True
