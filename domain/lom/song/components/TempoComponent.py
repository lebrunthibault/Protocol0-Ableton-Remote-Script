from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.shared.utils.timing import debounce
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class TempoComponent(SlotManager):
    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(TempoComponent, self).__init__()
        self._song = song
        self._tempo_listener.subject = self._song

    @subject_slot("tempo")
    @debounce(duration=1000)
    def _tempo_listener(self):
        # type: () -> None
        Scheduler.defer(partial(setattr, self, "tempo", round(self.tempo)))

    @property
    def tempo(self):
        # type: () -> float
        return self._song.tempo

    @tempo.setter
    def tempo(self, tempo):
        # type: (float) -> None
        try:
            self._song.tempo = tempo
        except RuntimeError:
            pass

    def tap(self):
        # type: () -> None
        self._song.tap_tempo()

    def scroll(self, go_next):
        # type: (bool) -> None
        increment = 1 if go_next else -1
        self.tempo += increment
