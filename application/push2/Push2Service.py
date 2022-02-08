from fractions import Fraction

from Push2.push2 import Push2
from typing import Optional, Any, List, cast

from _Framework.ControlSurface import get_control_surfaces
from _Framework.SubjectSlot import subject_slot_group, subject_slot
from protocol0.application.push2.decorators import push2_method
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class Push2Service(object):
    _ENABLE_AUTO_SELECTED_MODE = False
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
        self.push2 = None  # type: Optional[Push2]
        self.update_session_ring = True
        self.update_selected_modes = True

    def connect_push2(self, log=False):
        # type: (bool) -> None
        """ object modification, push2 registers itself after protocol0 instantiation """
        push2 = find_if(lambda cs: isinstance(cs, Push2), get_control_surfaces())
        if not push2 or not hasattr(push2, "_session_ring"):
            if log:
                Logger.log_warning("Cannot connect to push2")
            return

        if not self.push2:
            Logger.log_info("Push2 connected")

        self.push2 = push2
        with push2.component_guard():
            self.push2._session_ring.set_enabled(False)
            self.push2._matrix_modes.selected_mode = "session"
            self._session_pad_press_listener.subject = self.push2.elements.matrix
            self._track_select_button_press_listener.subject = self.push2.elements.select_buttons
            self._nav_button_press_listener.replace_subjects(
                [self.push2.elements.nav_left_button, self.push2.elements.nav_right_button]
            )

        if not self.push2:
            Logger.log_info("Push2 connected to Protocol0")

    @subject_slot("value")
    def _session_pad_press_listener(self, value, *_, **__):
        # type: (Any, Any, Any) -> None
        if value:
            self.update_session_ring = self.update_selected_modes = False

    @subject_slot("value")
    def _track_select_button_press_listener(self, value, *_, **__):
        # type: (Any, Any, Any) -> None
        if value:
            self.update_session_ring = False
            Scheduler.defer(self._update_selected_modes)

    @subject_slot_group("value")
    def _nav_button_press_listener(self, value, *a, **k):
        # type: (Any, Any, Any) -> None
        pass

    def _selected_track_listener(self):
        # type: () -> None
        # NB :  listen to this
        self._update_selected_modes()

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
        self.update_session_ring = True

    @push2_method()
    def update_clip_grid_quantization(self):
        # type: () -> None
        assert self.push2
        self._update_selected_modes()
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

    # noinspection PyUnresolvedReferences
    @push2_method()
    def _update_selected_modes(self):
        # type: () -> None
        if not self._ENABLE_AUTO_SELECTED_MODE:
            return
        assert self.push2
        if self.update_selected_modes and SongFacade.selected_track().IS_ACTIVE:
            self.push2._main_modes.selected_mode = SongFacade.selected_track().push2_selected_main_mode.label
            self.push2._matrix_modes.selected_mode = SongFacade.selected_track().push2_selected_matrix_mode.label
            if SongFacade.selected_track().push2_selected_instrument_mode:
                self.push2._instrument.selected_mode = SongFacade.selected_track().push2_selected_instrument_mode.label
            else:
                self.push2._instrument.selected_mode = self.push2._instrument.selected_mode

        self.update_selected_modes = True
