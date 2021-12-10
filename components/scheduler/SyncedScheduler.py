# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Embedded file name: C:\ProgramData\Ableton\Live 9.7 Suite\Resources\MIDI Remote Scripts\ClyphX_Pro\clyphx_pro\SyncedScheduler.py
# Compiled at: 2019-04-24 15:38:10
from ClyphX_Pro.ClyphXComponentBase import ClyphXComponentBase, schedule
from ClyphX_Pro.MiscUtils import get_number_of_beats
from typing import Any

from protocol0.utils.decorators import p0_subject_slot


class SyncedScheduler(ClyphXComponentBase):
    """ SyncedScheduler schedules action lists to be triggered after a specified
    number of bars. """

    def __init__(self, unschedule_on_stop, *a, **k):
        # type: (bool, Any, Any) -> None
        super(SyncedScheduler, self).__init__(*a, **k)
        self._unschedule_on_stop = unschedule_on_stop
        self._last_beat = -1
        self._pending_action_lists = {}
        self._on_is_playing_changed.subject = self._song
        self._on_song_time_changed.subject = self._song

    def schedule_message(self, text, msg):
        # type: (str, Any) -> None
        """ Schedules the given action_list to be triggered after the specified number
        of bars. """
        num_beats = get_number_of_beats(text, self._song, is_legacy_bar=True)
        count = int(self._song.get_current_beats_song_time().beats == self._last_beat)
        self._pending_action_lists[msg] = {'num_beats': num_beats, 'count': count}

    @p0_subject_slot('is_playing')
    def _on_is_playing_changed(self):
        # type: () -> None
        if not self._song.is_playing and self._unschedule_on_stop:
            self._pending_action_lists = {}
        self._last_beat = -1

    @p0_subject_slot('current_song_time')
    def _on_song_time_changed(self):
        # type: () -> None
        if self._pending_action_lists and self._song.is_playing:
            current_beat = self._song.get_current_beats_song_time().beats
            if self._last_beat != current_beat:
                self._last_beat = current_beat
                for k, v in self._pending_action_lists.items():
                    v['count'] += 1
                    if v['count'] > v['num_beats']:
                        schedule(k)
                        del self._pending_action_lists[k]

    def disconnect(self):
        # type: () -> None
        super(SyncedScheduler, self).disconnect()
        self._pending_action_lists = {}
        return
