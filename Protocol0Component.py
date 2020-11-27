import types
from typing import Optional, Callable

from _Framework.CompoundComponent import CompoundComponent
from _Framework.Dependency import inject, depends
from _Framework.Util import const
from a_protocol_0.actions.ActionManager import ActionManager
from a_protocol_0.actions.MidiActions import MidiActions
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class Protocol0Component(CompoundComponent):

    @depends(send_midi=None)
    def __init__(self, send_midi=None, *a, **k):
        super(Protocol0Component, self).__init__(*a, **k)
        # noinspection PyProtectedMember
        self.canonical_parent._c_instance.log_message = types.MethodType(lambda s, message: None, self.canonical_parent._c_instance)
        self._my_song = Song(self.song(), self)
        ActionManager(parent=self)
        with inject(send_midi=const(send_midi)).everywhere():
            self.midi = MidiActions()
            self.register_component(self.midi)
        self.log_message("Protocol0Component initialized")

    def my_song(self):
        # type: () -> Song
        return self._my_song

    @property
    def current_track(self):
        # type: () -> Optional[AbstractTrack]
        return self.my_song().current_track

    def log_message(self, message):
        # type: (str) -> None
        self.canonical_parent.log_message(message)

    def show_message(self, message):
        # type: (str) -> None
        self.canonical_parent.show_message(message)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        self.wait(self.my_song().delay_before_recording_end(bar_count), message)

    def wait(self, ticks_count, callback):
        # type: (int, Callable) -> None
        self.canonical_parent.schedule_message(ticks_count, callback)

    # noinspection PyProtectedMember
    def clear_tasks(self):
        del self.canonical_parent._remaining_scheduled_messages[:]
        self.canonical_parent._task_group.clear()

    def disconnect(self):
        super(Protocol0Component, self).disconnect()
