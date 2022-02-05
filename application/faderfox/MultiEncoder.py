import time

from typing import TYPE_CHECKING, List, Optional, Any

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from protocol0.application.service.decorators import handle_error
from protocol0.application.faderfox.EncoderAction import EncoderAction, EncoderMoveEnum
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from protocol0.application.faderfox.group.AbstractActionGroup import AbstractActionGroup


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

    @p0_subject_slot("value")
    @handle_error
    def _press_listener(self, value):
        # type: (int) -> None
        if value:
            if self._has_long_press:
                self._pressed_at = time.time()
            else:
                self._find_and_execute_action(move_type=EncoderMoveEnum.PRESS)
        else:
            if self._has_long_press:
                # action executed on press and not release when only press defined
                move_type = EncoderMoveEnum.LONG_PRESS if self._is_long_pressed else EncoderMoveEnum.PRESS
                self._find_and_execute_action(move_type=move_type)

    @p0_subject_slot("value")
    @handle_error
    def _scroll_listener(self, value):
        # type: (int) -> None
        self._find_and_execute_action(move_type=EncoderMoveEnum.SCROLL, go_next=value == 1)

    def _find_and_execute_action(self, move_type, go_next=None):
        # type: (EncoderMoveEnum, Optional[bool]) -> None
        action = self._find_matching_action(move_type=move_type)  # type: ignore[arg-type]
        self._pressed_at = None
        if not action:
            return None

        if self._filter_active_tracks and not self.song.selected_track.IS_ACTIVE:
            raise Protocol0Warning("action not dispatched for master / return tracks (%s)" % action.name)

        params = {}
        if go_next is not None:
            params["go_next"] = go_next  # type: ignore[assignment]

        action.execute(encoder_name=self.name, **params)

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
            raise Protocol0Warning("Action not found: %s (%s)" % (self.name, move_type))

        return action
