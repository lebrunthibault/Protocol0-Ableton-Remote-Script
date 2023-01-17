import json
import time

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import List, Optional, Callable

from protocol0.application.control_surface.EncoderAction import EncoderAction, EncoderMoveEnum
from protocol0.domain.lom.set.AbletonSetChangedEvent import AbletonSetChangedEvent
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class MultiEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(self, channel, identifier, name, filter_active_tracks, component_guard):
        # type: (int, int, str, bool, Callable) -> None
        """
        Actions are triggered at the end of the press not the start. Allows press vs long_press (Note) vs scroll (CC)
        NB : for press actions the action is triggered on button release (allowing long_press)
        """
        super(MultiEncoder, self).__init__()
        self._actions = []  # type: List[EncoderAction]
        self.identifier = identifier
        self.name = name.title()
        self._active = True
        self._channel = channel
        self._filter_active_tracks = filter_active_tracks

        with component_guard():
            self._press_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, channel, identifier)
            self._scroll_listener.subject = ButtonElement(True, MIDI_CC_TYPE, channel, identifier)
        self._pressed_at = None  # type: Optional[float]
        self._has_long_press = False

        DomainEventBus.subscribe(AbletonSetChangedEvent, self._on_script_state_changed_event)

    def _on_script_state_changed_event(self, event):
        # type: (AbletonSetChangedEvent) -> None
        self._active = event.set.active

    def __repr__(self):
        # type: () -> str
        return json.dumps({"channel": self._channel, "name": self.name, "id": self.identifier})

    def add_action(self, action):
        # type: (EncoderAction) -> MultiEncoder
        assert self._find_matching_action(action.move_type) is None, "duplicate move %s" % action
        if action.move_type == EncoderMoveEnum.LONG_PRESS:
            self._has_long_press = True
        self._actions.append(action)
        return self

    @property
    def _is_long_pressed(self):
        # type: () -> bool
        return bool(
            self._pressed_at
            and (time.time() - self._pressed_at) > MultiEncoder.LONG_PRESS_THRESHOLD
        )

    @subject_slot("value")
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
                move_type = (
                    EncoderMoveEnum.LONG_PRESS if self._is_long_pressed else EncoderMoveEnum.PRESS
                )
                self._find_and_execute_action(move_type=move_type)

    @subject_slot("value")
    def _scroll_listener(self, value):
        # type: (int) -> None
        self._find_and_execute_action(move_type=EncoderMoveEnum.SCROLL, go_next=value == 1)

    def _find_and_execute_action(self, move_type, go_next=None):
        # type: (EncoderMoveEnum, Optional[bool]) -> None
        # noinspection PyBroadException
        try:
            if not self._active:
                Logger.warning("The encoder '%s' is not activated" % self.name)
                return None

            action = self._find_matching_action(move_type=move_type)
            # special case : fallback long_press to press
            if not action and move_type == EncoderMoveEnum.LONG_PRESS:
                action = self._find_matching_action(move_type=EncoderMoveEnum.PRESS)

            if not action:
                raise Protocol0Warning("Action not found: %s (%s)" % (self.name, move_type))

            self._pressed_at = None
            if not action:
                return None

            selected_track = Song.selected_track()
            if self._filter_active_tracks and (
                selected_track is None or not selected_track.IS_ACTIVE
            ):
                raise Protocol0Warning(
                    "action not dispatched for master / return tracks (%s)" % action.name
                )

            params = {}
            if go_next is not None:
                params["go_next"] = go_next

            action.execute(encoder_name=self.name, **params)
        except Exception as e:  # noqa
            DomainEventBus.emit(ErrorRaisedEvent())

    def _find_matching_action(self, move_type):
        # type: (EncoderMoveEnum) -> Optional[EncoderAction]
        actions = [
            encoder_action
            for encoder_action in self._actions
            if encoder_action.move_type == move_type
        ]
        return next(iter(actions), None)
