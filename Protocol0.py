from __future__ import with_statement

from functools import partial

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *

from a_protocol_0.Protocol0Component import Protocol0Component
from a_protocol_0.utils.decorators import button_action


class Protocol0(Protocol0Component):

    def __init__(self, *a, **k):
        super(Protocol0, self).__init__(*a, **k)
        with self.component_guard():
            self.show_message('Protocol0 initiated')

            self.arm_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 1)
            self.sel_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 2)
            self.switch_monitoring_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 3)
            self.record_audio_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 4)
            self.record_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 5)
            # add rec2, 4, 8

            self.restart_set.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 12)
            self.scroll_tracks.subject = ButtonElement(True, MIDI_CC_TYPE, 15, 14)
            self.scroll_presets.subject = ButtonElement(True, MIDI_CC_TYPE, 15, 15)
            self.undo_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, 15, 16)

    @button_action()
    def arm_ext(self):
        """ arm or unarm both midi and audio track """
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
        """ arm both midi and audio track """
        self.current_track.switch_monitoring()

    @button_action()
    def record_ext(self, bar_count=1):
        """ record both midi and audio on group track """
        self.mySong().bar_count = int(bar_count)
        self.current_track.action_restart_and_record(self.current_track.action_record_all)

    @button_action()
    def record_audio_ext(self):
        """ record audio on group track from playing midi clip """
        self.current_track.action_restart_and_record(self.current_track.action_record_audio_only)

    @button_action()
    def restart_set(self):
        """" restart a live set from group tracks track names """
        self.mySong().restart_set()

    @button_action()
    def undo_ext(self):
        """" undo last recording """
        self.current_track.action_undo()

    @button_action(is_scrollable=True)
    def scroll_tracks(self, go_next):
        """ scroll top tracks """
        self.mySong().scroll_tracks(go_next)
        self.schedule_message(7, self.current_track.action_arm)

    @button_action(is_scrollable=True)
    def scroll_presets(self, go_next):
        """ scroll track device presets or samples """
        self.current_track.instrument.action_scroll_presets_or_samples(go_next)
