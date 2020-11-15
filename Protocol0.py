from __future__ import with_statement
import Live
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot

from a_protocol_0.Protocol0Component import Protocol0Component


class Protocol0(Protocol0Component):

    def __init__(self, *a, **k):
        super(Protocol0, self).__init__(*a, **k)
        with self.component_guard():
            self.show_message('Protocol0 initiated')
            arm_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, 9)
            self.arm_action.subject = arm_button

    @subject_slot('value')
    def arm_action(self, value):
        if not value:
            return

        if self.current_track.arm:
            self.current_track.action_unarm()
        else:
            self.current_track.action_arm()