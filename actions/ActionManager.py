from __future__ import with_statement

from typing import TYPE_CHECKING

from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.InputControlElement import *
from a_protocol_0.consts import RECORDING_TIME_ONLY_AUDIO
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.decorators import button_action

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class ActionManager(ControlSurfaceComponent):
    @depends(parent=None)
    def __init__(self, parent=None, *a, **k):
        super(ActionManager, self).__init__(*a, **k)
        self.parent = parent
        record_encoder = MultiEncoder(15, 9)
        record_encoder.on_scroll = self.scroll_recording_times
        record_encoder.on_press = self.record_ext

        track_encoder = MultiEncoder(15, 13)
        track_encoder.on_scroll = self.scroll_tracks
        track_encoder.on_press = self.arm_ext
        track_encoder.on_long_press = self.sel_ext

        device_encoder = MultiEncoder(15, 14)
        device_encoder.on_scroll = self.scroll_presets

        self.switch_monitoring_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 3)
        self.restart_set.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 12)
        self.undo_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 16)

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.parent.current_track

    @button_action()
    def arm_ext(self):
        """ arm or unarm both midi and audio track """
        if self.current_track.is_simple_group:
            self.current_track.is_folded = not self.current_track.is_folded
            return

        if self.current_track.arm:
            self.current_track.action_unarm()
        else:
            self.current_track.action_arm()

    @button_action()
    def sel_ext(self):
        """ Sel midi track to open ext editor """
        self.current_track.action_sel()

    @button_action()
    def switch_monitoring_ext(self):
        self.current_track.switch_monitoring()

    @button_action(is_scrollable=True)
    def scroll_recording_times(self, go_next):
        """ record both midi and audio on group track """
        increment = 1 if go_next else - 1
        if self.current_track.recording_time is not None:
            index = self.current_track.recording_times.index(self.current_track.recording_time) + increment
        else:
            index = 0

        value = self.current_track.recording_times[index % len(self.current_track.recording_times)]
        self.current_track.recording_time = value
        self.parent.show_message("Recording %s" % str(value))

    @button_action()
    def record_ext(self):
        """ record both midi and audio on group track """
        if self.current_track.recording_time == RECORDING_TIME_ONLY_AUDIO:
            return self.current_track.action_restart_and_record(self.current_track.action_record_audio_only, only_audio=True)
        else:
            self.current_track.bar_count = int(self.current_track.recording_time.split()[0])
            self.current_track.action_restart_and_record(self.current_track.action_record_all)

    @button_action()
    def restart_set(self):
        """" restart a live set from group tracks track names """
        self.parent.my_song().restart_set()

    @button_action()
    def undo_ext(self):
        """" undo last recording """
        self.current_track.action_undo()

    @button_action(is_scrollable=True, log_action=False)
    def scroll_tracks(self, go_next):
        """ scroll top tracks """
        self.parent.my_song().scroll_tracks(go_next)

    @button_action(is_scrollable=True)
    def scroll_presets(self, go_next):
        """ scroll track device presets or samples """
        if not self.current_track.selectable_track.is_selected:
            self.current_track.action_sel()
        self.current_track.instrument.action_scroll_presets_or_samples(go_next)
