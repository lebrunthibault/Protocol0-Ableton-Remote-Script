from fractions import Fraction

from _Framework.SubjectSlot import subject_slot_group, subject_slot, SlotManager
from typing import Optional, Any, List, cast

from protocol0.application.push2.Push2InitializedEvent import Push2InitializedEvent
from protocol0.application.push2.decorators import push2_method
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0_push2.push2 import Push2


class Push2Service(SlotManager):
    _DEBUG = True
    _PUSH2_BEAT_QUANTIZATION_STEPS = [
        Fraction(1, 48),
        Fraction(1, 32),
        Fraction(1, 24),
        Fraction(1, 16),
        Fraction(1, 12),
        Fraction(1, 8),
        Fraction(1, 6),
        Fraction(1, 4),
    ]

    def __init__(self):
        # type: () -> None
        super(Push2Service, self).__init__()
        self.push2 = None  # type: Optional[Push2]
        self._update_session_ring = True
        self._update_selected_modes = True
        DomainEventBus.subscribe(Push2InitializedEvent, self._on_push2_initialized_event)

    def _on_push2_initialized_event(self, event):
        # type: (Push2InitializedEvent) -> None
        """ push2 registers itself after protocol0 instantiation """
        Logger.info("Push2 connected to Protocol0")

        self.push2 = event.push2
        self.push2._session_ring.set_enabled(False)
        self.push2._matrix_modes.selected_mode = "session"
        self._track_select_button_press_listener.subject = self.push2.elements.select_buttons
        self._nav_button_press_listener.replace_subjects(
            [self.push2.elements.nav_left_button, self.push2.elements.nav_right_button]
        )

    @subject_slot("value")
    def _track_select_button_press_listener(self, value, *_, **__):
        # type: (Any, Any, Any) -> None
        if value:
            self._update_session_ring = False

    @subject_slot_group("value")
    def _nav_button_press_listener(self, value, *a, **k):
        # type: (Any, Any, Any) -> None
        pass

    @push2_method()
    def _update_session_ring(self):
        # type: () -> None
        assert self.push2
        # if self.update_session_ring:
        #     # noinspection PyBroadException
        #     try:
        #         # self.push2._session_ring.set_offsets(
        #         #     self.parent.sessionService.session.track_offset(), self.push2._session_ring.scene_offset
        #         # )
        #     except Exception:
        #         return
        self._update_session_ring = True

    @push2_method()
    def update_clip_grid_quantization(self):
        # type: () -> None
        assert self.push2
        quantization_index = self._get_notes_quantization_index(SongFacade.selected_midi_clip().get_notes())
        self.push2._grid_resolution.index = quantization_index
        self.push2._grid_resolution.quantization_buttons[quantization_index].is_checked = True

    def _get_note_quantization_index(self, note):
        # type: (Note) -> Optional[int]
        steps = [v * 4 for v in Push2Service._PUSH2_BEAT_QUANTIZATION_STEPS]
        for step in reversed(steps):
            if round(note.start / step, 6).is_integer():
                return steps.index(step)
        return None

    def _get_notes_quantization_index(self, notes):
        # type: (List[Note]) -> int
        notes_quantization_index = [self._get_note_quantization_index(note) for note in notes]
        if len(notes_quantization_index) == 0 or None in notes_quantization_index:
            return 3  # 1/16 by default
        else:
            return max(cast(List[int], notes_quantization_index))
