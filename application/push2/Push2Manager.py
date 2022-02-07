from Push2.push2 import Push2
from typing import Optional, cast, Any

from _Framework.ControlSurface import get_control_surfaces
from _Framework.SubjectSlot import subject_slot_group, subject_slot
from protocol0.application.push2.decorators import push2_method
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.note.NoteQuantizationManager import NoteQuantizationManager
from protocol0.domain.shared.utils import find_if
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class Push2Manager(object):
    ENABLE_AUTO_SELECTED_MODE = False

    def __init__(self, note_quantization_manager):
        # type: (NoteQuantizationManager) -> None
        self.note_quantization_manager = note_quantization_manager
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
        # if self.parent.sessionManager.session:
        #     self._update_session_ring()
        self._update_selected_modes()

    @push2_method()
    def _update_session_ring(self):
        # type: () -> None
        assert self.push2
        # if self.update_session_ring:
        #     # noinspection PyBroadException
        #     try:
        #         # self.push2._session_ring.set_offsets(
        #         #     self.parent.sessionManager.session.track_offset(), self.push2._session_ring.scene_offset
        #         # )
        #     except Exception:
        #         return
        self.update_session_ring = True

    @push2_method()
    def update_clip_grid_quantization(self):
        # type: () -> None
        assert self.push2
        if not SongFacade.selected_clip() or not isinstance(SongFacade.selected_clip(), MidiClip):
            return
        clip = cast(MidiClip, SongFacade.selected_clip())
        self._update_selected_modes()
        quantization_index = self.note_quantization_manager.get_notes_quantization_index(clip.get_notes())
        self.push2._grid_resolution.index = quantization_index
        self.push2._grid_resolution.quantization_buttons[quantization_index].is_checked = True

    # noinspection PyUnresolvedReferences
    @push2_method()
    def _update_selected_modes(self):
        # type: () -> None
        if not self.ENABLE_AUTO_SELECTED_MODE:
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
