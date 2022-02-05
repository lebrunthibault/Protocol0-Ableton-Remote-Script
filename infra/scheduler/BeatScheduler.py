from typing import Callable, Any, Optional

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.infra.scheduler.SyncedScheduler import SyncedScheduler
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.lom.AbstractObject import AbstractObject


class BeatScheduler(AbstractObject, SyncedScheduler):
    _INSTANCE = None  # type: Optional[BeatScheduler]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        if self._INSTANCE:
            raise Protocol0Error("BeatScheduler singleton already created")

        super(BeatScheduler, self).__init__(unschedule_on_stop=True, *a, **k)

    @classmethod
    def get_instance(cls):
        # type: () -> BeatScheduler
        if not cls._INSTANCE:
            cls._INSTANCE = BeatScheduler()

        return cls._INSTANCE

    def wait_bars(self, bar_length, callback):
        # type: (int, Callable) -> None
        """
        if exact if False, wait_bars executes the callback on the last beat preceding the next <bar_length> bar
        that is if the we are on the 3rd beat in 4/4, the callback will be executed in one beat
        This mode will work when global quantization is set to 1/4 or more
        """
        self.wait_beats(self.song.signature_numerator * bar_length, callback)

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        # deferring in the case we call wait_beats just after starting the song
        self.parent.defer(self._check_song_is_playing)
        self.schedule_message(beats, callback)

    def _check_song_is_playing(self):
        # type: () -> None
        if not self.song.is_playing:
            raise Protocol0Warning("Called wait_beat but song is not playing")

    def clear_scheduler(self):
        # type: () -> None
        self._pending_action_list.clear()
        self._pending_precise_action_list.clear()
