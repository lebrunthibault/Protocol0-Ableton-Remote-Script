from math import floor

from ClyphX_Pro.ClyphXComponentBase import ClyphXComponentBase, schedule
from typing import Any, Optional

from protocol0.utils.decorators import p0_subject_slot


class SyncedScheduler(ClyphXComponentBase):
    """ SyncedScheduler schedules action lists to be triggered after a specified
    number of bars. """

    def __init__(self, unschedule_on_stop, *a, **k):
        # type: (bool, Any, Any) -> None
        super(SyncedScheduler, self).__init__(*a, **k)
        self._unschedule_on_stop = unschedule_on_stop
        self._last_beat = None  # type: Optional[int]
        self._last_sixteenth = None  # type: Optional[int]
        self._pending_action_list = {}
        self._pending_precise_action_list = {}
        self._on_is_playing_changed.subject = self._song
        self._on_song_time_changed.subject = self._song

    def schedule_message(self, num_beats, msg):
        # type: (float, Any) -> None
        """ Schedules the given action_list to be triggered after the specified number
        of bars. """
        action = {'beats': num_beats, 'sixteenths': 0, 'ticks': 0}
        if float(num_beats).is_integer():
            self._pending_action_list[msg] = action
        else:
            beats = floor(num_beats)
            beats_reminder = (num_beats - beats)
            sixteenth_float_value = float(1) / self.song.signature_numerator
            tick_float_value = float(1) / 60

            sixteenths = beats_reminder // sixteenth_float_value
            sixteenths_float_reminder = beats_reminder % sixteenth_float_value
            ticks = sixteenths_float_reminder // tick_float_value

            action["beats"] = beats
            action["sixteenths"] = sixteenths
            action["ticks"] = ticks

            self._pending_precise_action_list[msg] = action

    @p0_subject_slot('is_playing')
    def _on_is_playing_changed(self):
        # type: () -> None
        if not self._song.is_playing and self._unschedule_on_stop:
            self._pending_action_list = {}
        self._last_beat = -1

    @p0_subject_slot('current_song_time')
    def _on_song_time_changed(self):
        # type: () -> None
        if not self._song.is_playing:
            return

        current_beat_time = self._song.get_current_beats_song_time()
        current_beat = current_beat_time.beats
        current_sixteenth = current_beat_time.sub_division
        current_tick = current_beat_time.ticks

        for k, v in self._pending_precise_action_list.items():
            if v['beats'] == 0 and v['sixteenths'] == 0 and current_tick > v['ticks']:
                schedule(k)
                del self._pending_precise_action_list[k]

        if self._last_sixteenth != current_sixteenth:
            self._last_sixteenth = current_sixteenth
            for k, v in self._pending_precise_action_list.items():
                if v['beats'] == 0:
                    v['sixteenths'] -= 1
                if v['sixteenths'] < 0:
                    schedule(k)
                    del self._pending_precise_action_list[k]

        if self._last_beat != current_beat:
            self._last_beat = current_beat

            self._on_beat_changed()

            for k, v in self._pending_precise_action_list.items():
                v['beats'] -= 1

            for k, v in self._pending_action_list.items():
                v['beats'] -= 1
                if v['beats'] == 0:
                    schedule(k)
                    del self._pending_action_list[k]

    def _on_beat_changed(self):
        # type: () -> None
        if self.song.playing_scene and self.song.playing_scene.has_playing_clips:
            self.song.playing_scene.on_beat_changed()

    def disconnect(self):
        # type: () -> None
        super(SyncedScheduler, self).disconnect()
        self._pending_action_list = {}
        return
