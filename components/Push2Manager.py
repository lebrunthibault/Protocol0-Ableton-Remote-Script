from typing import Optional

from a_Push2.push2 import Push2
from a_Push2.track_list import TrackListComponent
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import push2_method, augment


class Push2Manager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(Push2Manager, self).__init__(*a, **k)
        self.push2 = None  # type: Optional[Push2]
        self._augment_push2_script()

    def _augment_push2_script(self):
        """ class / static augmentation """
        TrackListComponent._select_mixable = augment(TrackListComponent._select_mixable,
                                                     self.update_mode_for_current_track)

    def connect_push2(self, push2):
        # type: (Push2) -> None
        """ object modification, push2 registers itself after protocol0 instantiation """
        self.push2 = push2
        self.push2._session_ring.set_enabled(False)
        self.push2._matrix_modes.selected_mode = 'session'

    @push2_method()
    def update_session_ring(self):
        self.push2._session_ring.set_offsets(self.parent.sessionManager.session_track_offset,
                                           self.push2._session_ring.scene_offset)

    @push2_method()
    def update_mode_for_current_track(self):
        # type: () -> None
        self.push2._matrix_modes.selected_mode = 'session'
        self.push2._main_modes.selected_mode = 'device'
        if self.current_track.is_foldable and not self.current_track.is_external_synth_track:
            self.push2._main_modes.selected_mode = 'mix'
        elif self.current_track.is_midi:
            self.push2._matrix_modes.selected_mode = 'note'
            self.push2._instrument.selected_mode = 'split_melodic_sequencer'

