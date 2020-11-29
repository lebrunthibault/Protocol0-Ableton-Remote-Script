import time

from _Framework.ButtonElement import ButtonElement
from _Framework.Control import SlotManager
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot


class MultiEncoder(SlotManager):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press

    def __init__(self, channel, identifier):
        # type: (int, int) -> None
        super(MultiEncoder, self).__init__()
        self.channel = channel
        self.identifier = identifier
        self._on_multi_press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, self.channel, self.identifier)
        self.on_press = None
        self.on_long_press = None
        self.pressed_at = 0  # type: float

    @property
    def on_scroll(self):
        return None

    @on_scroll.setter
    def on_scroll(self, listener):
        listener.subject = ButtonElement(True, MIDI_CC_TYPE, self.channel, self.identifier)

    @subject_slot("value")
    def _on_multi_press_listener(self, value):
        if value:
            self.pressed_at = time.time()
            return
        press_time = time.time() - self.pressed_at

        if press_time <= MultiEncoder.PRESS_MAX_TIME and self.on_press:
            self.on_press(127)
        elif self.on_long_press:
            self.on_long_press(127)
