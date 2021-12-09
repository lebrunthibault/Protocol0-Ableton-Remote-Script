import time

from typing import TYPE_CHECKING, List, Optional, Any

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot
from protocol0.interface.EncoderAction import EncoderAction, EncoderMoveEnum
from protocol0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class MultiEncoder(AbstractObject):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press

    def __init__(self, group, identifier, name, filter_active_tracks, *a, **k):
        # type: (AbstractActionGroup, int, str, bool, Any, Any) -> None
        """
        Actions are triggered at the end of the press not the start. Allows press vs long_press (Note) vs scroll (CC)
        NB : for press actions the action is triggered on button release (allowing long_press)
        """
        super(MultiEncoder, self).__init__(*a, **k)
        self._actions = []  # type: List[EncoderAction]
        self.identifier = identifier
        self.name = name.title()
        self._filter_active_tracks = filter_active_tracks
        self._press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, group.channel, identifier)
        self._scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, group.channel, identifier)
        self._pressed_at = None  # type: Optional[float]
        self._has_long_press = False

    def add_action(self, action):
        # type: (EncoderAction) -> MultiEncoder
        assert not self._find_matching_action(
            action.move_type, exact_match=True, log_not_found=False
        ), ("duplicate move %s" % action)
        if action.move_type == EncoderMoveEnum.LONG_PRESS:
            self._has_long_press = True
        self._actions.append(action)
        return self

    @property
    def _is_long_pressed(self):
        # type: () -> bool
        return bool(self._pressed_at and (time.time() - self._pressed_at) > MultiEncoder.PRESS_MAX_TIME)

    @subject_slot("value")
    def _press_listener(self, value):
        # type: (int) -> None
        if value:
            if self._has_long_press:
                self._pressed_at = time.time()
            else:
                self._find_and_execute_action()
        else:
            if self._has_long_press:
                # action executed on press and not release when only press defined
                self._find_and_execute_action()

    def _find_and_execute_action(self):
        # type: () -> None
        move_type = EncoderMoveEnum.LONG_PRESS if self._is_long_pressed else EncoderMoveEnum.PRESS
        action = self._find_matching_action(move_type=move_type)  # type: ignore[arg-type]
        self._pressed_at = None
        if action:
            if self._filter_active_tracks and not self.song.selected_track.is_active:
                self.parent.show_message("actions are not dispatched for master / return tracks")
                return
            action.execute(encoder_name=self.name)

    @subject_slot("value")
    def _scroll_listener(self, value):
        # type: (int) -> None
        action = self._find_matching_action(move_type=EncoderMoveEnum.SCROLL)  # type: ignore[arg-type]
        if action:
            action.execute(encoder_name=self.name, go_next=value == 1)

    def _find_matching_action(self, move_type, exact_match=False, log_not_found=True):
        # type: (EncoderMoveEnum, bool, bool) -> Optional[EncoderAction]
        def find_matching_action(inner_move_type):
            # type: (EncoderMoveEnum) -> Optional[EncoderAction]
            actions = [
                encoder_action
                for encoder_action in self._actions
                if encoder_action.move_type == inner_move_type
            ]
            return next(iter(actions), None)

        action = find_matching_action(inner_move_type=move_type)  # type: ignore[arg-type]

        # special case : fallback long_press to press
        if not action and move_type == EncoderMoveEnum.LONG_PRESS and not exact_match:
            # type: ignore[arg-type]
            action = find_matching_action(inner_move_type=EncoderMoveEnum.PRESS)

        if not action and log_not_found:
            self.parent.show_message(
                "Press didn't trigger action, move_type: %s" % move_type
            )

        return action
