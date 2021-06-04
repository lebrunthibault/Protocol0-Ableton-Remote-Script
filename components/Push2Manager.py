from typing import Optional, cast, Any

from _Framework.SubjectSlot import subject_slot, subject_slot_group
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.utils.decorators import push2_method
from a_push2.push2 import Push2


class Push2Manager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(Push2Manager, self).__init__(*a, **k)
        self.push2 = None  # type: Optional[Push2]
        self.update_session_ring = True
        self.update_selected_modes = True
        self._selected_track_listener.subject = self.parent.songManager

    def connect_push2(self, push2):
        # type: (Push2) -> None
        """ object modification, push2 registers itself after protocol0 instantiation """
        self.push2 = push2
        self.push2._session_ring.set_enabled(False)
        self.push2._matrix_modes.selected_mode = "session"
        self._session_pad_press_listener.subject = self.push2.elements.matrix
        self._track_select_button_press_listener.subject = self.push2.elements.select_buttons
        self._nav_button_press_listener.replace_subjects(
            [self.push2.elements.nav_left_button, self.push2.elements.nav_right_button]
        )
        self.parent.log_info("Push2 connected to Protocol0")
        self.parent.post_init()

    @subject_slot("value")
    def _session_pad_press_listener(self, value, *a, **k):
        # type: (Any, Any, Any) -> None
        if value:
            self.update_session_ring = self.update_selected_modes = False

    @subject_slot("value")
    def _track_select_button_press_listener(self, value, *a, **k):
        # type: (Any, Any, Any) -> None
        if value:
            self.update_session_ring = False
            self.parent.defer(self._update_selected_modes)

    @subject_slot_group("value")
    def _nav_button_press_listener(self, value, *a, **k):
        # type: (Any, Any, Any) -> None
        pass

    @subject_slot("selected_track")
    def _selected_track_listener(self):
        # type: () -> None
        if self.parent.sessionManager.session:
            self._update_session_ring()
        self._update_selected_modes()

    @push2_method()
    def _update_session_ring(self):
        # type: () -> None
        assert self.push2
        if self.update_session_ring:
            # noinspection PyBroadException
            try:
                self.push2._session_ring.set_offsets(
                    self.parent.sessionManager.session.track_offset(), self.push2._session_ring.scene_offset
                )
            except Exception:
                return
        self.update_session_ring = True

    @push2_method()
    def update_clip_grid_quantization(self):
        # type: () -> None
        assert self.push2
        if not self.song.selected_clip or not self.song.selected_clip.is_midi:
            return
        clip = cast(MidiClip, self.song.selected_clip)
        self._update_selected_modes()
        self.push2._grid_resolution.index = clip.quantization_index
        self.push2._grid_resolution.quantization_buttons[clip.quantization_index].is_checked = True

    @push2_method()
    def _update_selected_modes(self):
        # type: () -> None
        assert self.push2
        if self.update_selected_modes and self.song.selected_track.is_active:
            self.push2._main_modes.selected_mode = self.song.selected_track.push2_selected_main_mode
            self.push2._matrix_modes.selected_mode = self.song.selected_track.push2_selected_matrix_mode
            self.push2._instrument.selected_mode = (
                self.song.selected_track.push2_selected_instrument_mode or self.push2._instrument.selected_mode
            )

        self.update_selected_modes = True
