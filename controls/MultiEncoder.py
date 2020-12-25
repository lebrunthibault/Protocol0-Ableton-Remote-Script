import time

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.AbstractObject import AbstractObject


class MultiEncoder(AbstractObject):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press
    SHIFT_PRESSED = False

    def __init__(self, channel, identifier, on_press=None, on_release=None, on_long_press=None, on_shift_press=None, on_scroll=None, on_shift_scroll=None):
        # type: (int, int) -> None
        """ on release combined with on_press allows for immediate action and release action. Used for shift functionality """
        super(MultiEncoder, self).__init__()
        self.channel = channel
        self.identifier = identifier
        self.on_press = on_press
        self.on_release = on_release
        self.on_long_press = on_long_press
        self.on_shift_press = on_shift_press
        self.on_scroll = on_scroll
        self.on_shift_scroll = on_shift_scroll
        self._press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, self.channel, self.identifier)
        self._scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, self.channel, self.identifier)
        self.pressed_at = 0  # type: float
        self.is_pressed = False

    @subject_slot("value")
    def _press_listener(self, value):
        if value:
            if self.on_release:
                self.on_press()
            self.pressed_at = time.time()
            self.is_pressed = True
            return
        self.is_pressed = False
        press_time = time.time() - self.pressed_at

        if press_time > MultiEncoder.PRESS_MAX_TIME and self.on_long_press:
            self.on_long_press()
        elif self.SHIFT_PRESSED and self.on_shift_press:
            self.on_shift_press()
        elif self.on_release:
            self.on_release()
        elif self.on_press:
            self.on_press()

    @subject_slot("value")
    def _scroll_listener(self, value):
        if self.SHIFT_PRESSED and self.on_shift_scroll:
            self.on_shift_scroll(go_next=value == 1)
        elif self.on_scroll:
            self.on_scroll(go_next=value == 1)
