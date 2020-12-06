import time

from _Framework.ButtonElement import ButtonElement
from _Framework.Control import SlotManager
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject


class MultiEncoder(SlotManager, AbstractObject):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press

    def __init__(self, channel, identifier, on_press=None, on_long_press=None, on_scroll=None):
        # type: (int, int) -> None
        super(MultiEncoder, self).__init__()
        self.channel = channel
        self.identifier = identifier
        self.on_press = on_press
        self.on_long_press = on_long_press
        self.on_scroll = on_scroll
        self._on_multi_press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, self.channel, self.identifier)
        self._on_multi_scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, self.channel, self.identifier)
        self.pressed_at = 0  # type: float
        self.is_pressed = False

    @subject_slot("value")
    def _on_multi_press_listener(self, value):
        if value:
            self.pressed_at = time.time()
            self.is_pressed = True
            return
        self.is_pressed = False
        press_time = time.time() - self.pressed_at

        if press_time > MultiEncoder.PRESS_MAX_TIME and self.on_long_press:
            self.on_long_press(127)
        elif self.on_press:
            self.on_press(127)

    @subject_slot("value")
    def _on_multi_scroll_listener(self, value):
        if self.on_scroll:
            self.on_scroll(go_next=value == 1)
