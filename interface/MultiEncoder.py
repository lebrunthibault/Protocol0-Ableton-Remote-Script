import time

from typing import TYPE_CHECKING, List, Optional, Any

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot
from a_protocol_0.interface.EncoderAction import EncoderAction, EncoderMoveEnum
from a_protocol_0.interface.EncoderModifier import EncoderModifier
from a_protocol_0.interface.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup


class MultiEncoder(AbstractObject):
    PRESS_MAX_TIME = 0.25  # maximum time in seconds we consider a simple press

    def __init__(self, group, identifier, name, filter_active_tracks=True, *a, **k):
        # type: (AbstractActionGroup, int, str, bool, Any, Any) -> None
        """
        Actions are triggered at the end of the press not the start. Allows press vs long_press (Note) vs scroll (CC)
        Also possible to define modifiers to duplicate the number of actions possible.
        NB : for press actions the action is triggered on button release (allowing long_press)
        """
        super(MultiEncoder, self).__init__(*a, **k)
        self._actions = []  # type: List[EncoderAction]
        self._group = group  # type: AbstractActionGroup
        self.identifier = identifier
        self.name = name[0].upper() + name[1:].lower()
        self._filter_active_tracks = (
            group.filter_active_tracks if not group.filter_active_tracks else filter_active_tracks
        )
        self._press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, group.channel, identifier)
        self._scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, group.channel, identifier)
        self._pressed_at = None  # type: Optional[float]

    def get_modifier_from_enum(self, modifier_type):
        # type: (EncoderModifierEnum) -> EncoderModifier
        return [modifier for modifier in self._group.available_modifiers if modifier.type == modifier_type][0]

    def add_action(self, action):
        # type: (EncoderAction) -> MultiEncoder
        assert not self._find_matching_action(
            action.move_type, action.modifier_type, exact_match=True, log_not_found=False
        ), ("duplicate move %s" % action)
        self._actions.append(action)
        return self

    @property
    def _pressed_modifier_type(self):
        # type: () -> Optional[EncoderModifierEnum]
        pressed_modifiers = [modifier for modifier in self._group.available_modifiers if modifier.pressed]
        assert len(pressed_modifiers) <= 1, "Multiple modifiers pressed. Not allowed."
        return pressed_modifiers[0].type if len(pressed_modifiers) else None

    @property
    def _is_long_pressed(self):
        # type: () -> bool
        return bool(self._pressed_at and (time.time() - self._pressed_at) > MultiEncoder.PRESS_MAX_TIME)

    @subject_slot("value")
    def _press_listener(self, value):
        # type: (int) -> None
        if value:
            self._pressed_at = time.time()
            return

        move_type = EncoderMoveEnum.LONG_PRESS if self._is_long_pressed else EncoderMoveEnum.PRESS
        action = self._find_matching_action(move_type=move_type)
        self._pressed_at = None
        if action:
            if self._filter_active_tracks and not self.song.selected_track.is_active:
                self.parent.show_message("actions are not dispatched for master / return tracks")
                return
            action.execute(encoder_name=self.name)

    @subject_slot("value")
    def _scroll_listener(self, value):
        # type: (int) -> None
        action = self._find_matching_action(move_type=EncoderMoveEnum.SCROLL)
        if action:
            action.execute(encoder_name=self.name, go_next=value == 1)

    def _find_matching_action(self, move_type, modifier_type=None, exact_match=False, log_not_found=True):
        # type: (EncoderMoveEnum, Optional[EncoderModifierEnum], bool, bool) -> Optional[EncoderAction]
        modifier_type = modifier_type or self._pressed_modifier_type

        def find_matching_action(move_type, modifier_type):
            # type: (EncoderMoveEnum, EncoderModifierEnum) -> Optional[EncoderAction]
            actions = [
                action
                for action in self._actions
                if action.move_type == move_type and action.modifier_type == modifier_type
            ]
            return next(iter(actions), None)

        action = find_matching_action(move_type=move_type, modifier_type=modifier_type)

        # special case press reacts to long_press when no matching action is found
        if move_type == EncoderMoveEnum.LONG_PRESS and not exact_match:
            action = find_matching_action(move_type=EncoderMoveEnum.PRESS, modifier_type=modifier_type)

        if not action and log_not_found:
            self.parent.show_message(
                "Press didn't trigger action, move_type: %s, modifier: %s" % (move_type, self._pressed_modifier_type)
            )

        return action
