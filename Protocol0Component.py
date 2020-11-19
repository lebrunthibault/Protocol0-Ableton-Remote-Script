from typing import Optional, Callable

from _Framework.ControlSurface import ControlSurface

from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class Protocol0Component(ControlSurface):

    def __init__(self, *a, **k):
        super(Protocol0Component, self).__init__(*a, **k)
        self._my_song = Song(self.song(), self)
        self.log("Protocol0Component initialized")

    def my_song(self):
        # type: () -> Song
        return self._my_song

    @property
    def current_track(self):
        # type: () -> Optional[AbstractTrack]
        return self.my_song().current_track

    def log(self, message):
        # type: (str) -> None
        self.log_message(message)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        self.schedule_message(self.my_song().delay_before_recording_end(bar_count), message)

    def wait(self, ticks_count, message):
        # type: (int, Callable) -> None
        self.schedule_message(ticks_count, message)

    def clear_tasks(self):
        del self._remaining_scheduled_messages[:]
        self._task_group.clear()

    def disconnect(self):
        ControlSurface.disconnect(self)