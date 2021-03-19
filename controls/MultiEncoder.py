import time
from typing import TYPE_CHECKING

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from _Framework.SubjectSlot import subject_slot

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import catch_and_log

if TYPE_CHECKING:
    from a_protocol_0.components.actionManagers.AbstractActionManager import AbstractActionManager


class MultiEncoder(AbstractObject):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press
    SHIFT_PRESSED = False

    def __init__(self, action_manager, channel, id, on_press=None, on_release=None, on_long_press=None, on_shift_press=None,
                 on_shift_long_press=None, on_scroll=None, on_shift_scroll=None, *a, **k):
        """
            Actions are triggered at the end of the press not the start. Allows press vs long_press
            on release combined with on_press allows for immediate action and release action. Used for shift functionality
        """
        super(MultiEncoder, self).__init__(*a, **k)
        self.action_manager = action_manager  # type: AbstractActionManager
        self.channel = channel
        self.identifier = id
        self.on_press = on_press
        self.on_release = on_release
        self.on_long_press = on_long_press
        if not self.on_long_press and not self.on_release:
            self.on_long_press = on_press
        self.on_shift_press = on_shift_press
        self.on_shift_long_press = on_shift_long_press or on_shift_press
        self.on_scroll = on_scroll
        self.on_shift_scroll = on_shift_scroll
        self._press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, self.channel, self.identifier)
        self._scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, self.channel, self.identifier)
        self.pressed_at = 0  # type: float
        self.is_pressed = False

    @subject_slot("value")
    @catch_and_log
    def _press_listener(self, value):
        # type: (int) -> None
        if value:
            # only for shift action
            if self.on_release:
                self.on_press()
            self.pressed_at = time.time()
            self.is_pressed = True
            return

        self.is_pressed = False
        action = self._get_action()
        self.action_manager.current_action = action
        action()

    def _get_action(self):
        # type: () -> callable
        long_press = (time.time() - self.pressed_at) > MultiEncoder.PRESS_MAX_TIME

        if long_press and self.SHIFT_PRESSED and self.on_shift_long_press:
            return self.on_shift_long_press
        elif long_press and self.on_long_press:
            return self.on_long_press
        elif self.SHIFT_PRESSED and self.on_shift_press:
            return self.on_shift_press
        # on release if reachable only when long presses and shift presses are not setup
        elif self.on_release:
            return self.on_release
        elif self.on_press:
            return self.on_press

        raise Protocol0Error("Press didn't trigger action", {
            "press_time": time.time() - self.pressed_at,
            "long_press": long_press,
            "shift_press": self.SHIFT_PRESSED
        })

    @subject_slot("value")
    def _scroll_listener(self, value):
        if self.SHIFT_PRESSED and self.on_shift_scroll:
            self.on_shift_scroll(go_next=value == 1)
        elif self.on_scroll:
            self.on_scroll(go_next=value == 1)
