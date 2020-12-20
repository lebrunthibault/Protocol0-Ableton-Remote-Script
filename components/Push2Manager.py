from typing import Optional

from _Framework.SubjectSlot import subject_slot, subject_slot_group
from a_Push2.push2 import Push2
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import push2_beat_quantization_steps
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.utils.decorators import push2_method


class Push2Manager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(Push2Manager, self).__init__(*a, **k)
        self.push2 = None  # type: Optional[Push2]
        self.update_session_ring = True
        self.update_selected_modes = True

    def connect_push2(self, push2):
        # type: (Push2) -> None
        """ object modification, push2 registers itself after protocol0 instantiation """
        self.push2 = push2
        self.push2._session_ring.set_enabled(False)
        self.push2._matrix_modes.selected_mode = 'session'
        self._session_pad_press_listener.subject = self.push2.elements.matrix
        self._track_select_button_press_listener.subject = self.push2.elements.select_buttons
        self._nav_button_press_listener.replace_subjects([
            self.push2.elements.nav_left_button,
            self.push2.elements.nav_right_button
        ])
        self.song.select_track(self.song.tracks[0])
        self.parent.log_info("Push2 connected to Protocol0")
        self.parent.post_init()

    @subject_slot("value")
    def _session_pad_press_listener(self, value, *a, **k):
        if value:
            self.update_session_ring = self.update_selected_modes = self.parent.songManager.update_highlighted_clip_slot = False

    @subject_slot("value")
    def _track_select_button_press_listener(self, value, *a, **k):
        if value:
            self.update_session_ring = False
            self.parent.defer(lambda: self._update_selected_modes(reselect=True))

    @subject_slot_group("value")
    def _nav_button_press_listener(self, value, *a, **k):
        self.parent.log_debug(value)

    @push2_method(defer=False)
    def on_selected_track_changed(self):
        self._update_session_ring()
        self._update_selected_modes()

    @push2_method()
    def _update_session_ring(self):
        if self.update_session_ring:
            self.push2._session_ring.set_offsets(self.parent.sessionManager.session.track_offset(),
                                                 self.push2._session_ring.scene_offset)
        self.update_session_ring = True

    @push2_method()
    def update_clip_grid_quantization(self):
        # type: () -> Clip
        if not self.song.highlighted_clip_slot.has_clip:
            return
        index = push2_beat_quantization_steps.index(self.song.highlighted_clip_slot.clip.min_note_quantization_start)
        self.push2._grid_resolution.index = index
        self.push2._grid_resolution.quantization_buttons[index].is_checked = True

    @push2_method()
    def _update_selected_modes(self, reselect=False):
        # type: (bool) -> None
        if self.update_selected_modes:
            selected_main_mode = 'device'
            selected_matrix_mode = 'session'
            selected_instrument_mode = self.push2._instrument.selected_mode

            if self.song.current_track.is_simple_group:
                selected_main_mode = 'mix'
            elif self.song.current_track.is_automation:
                selected_main_mode = 'clip'
                selected_matrix_mode = 'note'
                selected_instrument_mode = 'split_melodic_sequencer'
            elif self.song.current_track.is_midi:
                selected_matrix_mode = 'note'
                selected_instrument_mode = 'split_melodic_sequencer'

            self.push2._main_modes.selected_mode = selected_main_mode
            self.push2._matrix_modes.selected_mode = selected_matrix_mode
            self.push2._instrument.selected_mode = selected_instrument_mode

            # See https://trello.com/c/0PUwHZOs/102-push2-bug-setting-selected-matrix-mode-after-clicking-on-session-ring-arrow-messes-selected-track
            if reselect:
                self.update_selected_modes = False
                self.song.select_track(self.song.current_track)

        self.update_selected_modes = True
