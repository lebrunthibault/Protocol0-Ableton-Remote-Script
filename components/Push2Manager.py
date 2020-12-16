from typing import Optional

from _Framework.SubjectSlot import subject_slot
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
        self.update_highlighted_clip = True

    def connect_push2(self, push2):
        # type: (Push2) -> None
        """ object modification, push2 registers itself after protocol0 instantiation """
        self.push2 = push2
        self.push2._session_ring.set_enabled(False)
        self.push2._matrix_modes.selected_mode = 'session'
        self._on_session_pad_press.subject = self.push2.elements.matrix
        self._on_track_select_button_press.subject = self.push2.elements.select_buttons
        # this needs to be delayed after push instantiation
        self.song.select_track(self.song.tracks[0])
        self.parent.sessionManager.set_enabled(True)
        self.parent.log_info("Push2 connected to Protocol0")
        self.parent.post_init()

    @subject_slot("value")
    def _on_session_pad_press(self, value, *a, **k):
        if value:
            self.update_session_ring = self.update_selected_modes = self.update_highlighted_clip = False
        if self.song.selected_track.is_automation:
            pass

    @subject_slot("value")
    def _on_track_select_button_press(self, value, *a, **k):
        if value:
            self.update_session_ring = self.update_selected_modes = self.update_highlighted_clip = False
            self._update_selected_modes()  # calling here to have it it change when on the same track
            self._update_highlighted_clip()  # calling here to have it it change when on the same track

    def on_selected_track_changed(self):
        if not self.push2:
            return
        if self.update_session_ring:
            self._update_session_ring()
        self.update_session_ring = True
        if self.update_selected_modes:
            self._update_selected_modes()
        self.update_selected_modes = True
        if self.update_highlighted_clip:
            self._update_highlighted_clip()
        self.update_highlighted_clip = True

    @push2_method()
    def _update_session_ring(self):
        self.push2._session_ring.set_offsets(self.parent.sessionManager.session.track_offset(),
                                             self.push2._session_ring.scene_offset)

    @push2_method()
    def _update_highlighted_clip(self):
        track = self.song.selected_track
        if track and track.is_visible and track.playable_clip:
            self.song.highlighted_clip_slot = track.playable_clip.clip_slot

    def update_clip_grid_quantization(self, clip):
        # type: () -> Clip
        index = push2_beat_quantization_steps.index(clip.min_note_quantization_start)
        self.push2._grid_resolution.quantization_buttons[index].is_checked = True

    @push2_method()
    def _update_selected_modes(self):
        # type: () -> None
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
