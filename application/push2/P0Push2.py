from fractions import Fraction

from protocol0_push2.push2 import Push2
from pushbase.push_base import NUM_TRACKS, NUM_SCENES
from typing import Optional, List, cast

from protocol0.application.push2.P0SessionNavigationComponent import P0SessionNavigationComponent
from protocol0.application.push2.P0SessionRingTrackProvider import P0SessionRingTrackProvider
from protocol0.domain.lom.note.Note import Note
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class P0Push2(Push2):
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

    def initialize(self):
        # type: () -> None
        super(P0Push2, self).initialize()
        Logger.info("Push2 connected to Protocol0")
        self._matrix_modes.selected_mode = "session"

    def _init_session_ring(self):
        # type: () -> None
        self._session_ring = P0SessionRingTrackProvider(name=u'Session_Ring', num_tracks=NUM_TRACKS,
                                                        num_scenes=NUM_SCENES, is_enabled=True)

    def _init_session(self):
        # type: () -> None
        super(P0Push2, self)._init_session()
        self._session_navigation = P0SessionNavigationComponent(session_ring=self._session_ring, is_enabled=False,
                                                                layer=self._create_session_navigation_layer())

    def update_clip_grid_quantization(self):
        # type: () -> None
        quantization_index = self._get_notes_quantization_index(SongFacade.selected_midi_clip().get_notes())
        self._grid_resolution.index = quantization_index
        self._grid_resolution.quantization_buttons[quantization_index].is_checked = True

    def _get_notes_quantization_index(self, notes):
        # type: (List[Note]) -> int
        def get_note_quantization_index(n):
            # type: (Note) -> Optional[int]
            steps = [v * 4 for v in self._PUSH2_BEAT_QUANTIZATION_STEPS]
            for step in reversed(steps):
                if round(n.start / step, 6).is_integer():
                    return steps.index(step)
            return None

        notes_quantization_index = [get_note_quantization_index(note) for note in notes]
        if len(notes_quantization_index) == 0 or None in notes_quantization_index:
            return 3  # 1/16 by default
        else:
            return max(cast(List[int], notes_quantization_index))
