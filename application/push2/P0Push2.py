from fractions import Fraction

import Live

from protocol0.application.push2.P0SessionNavigationComponent import P0SessionNavigationComponent
from protocol0.application.push2.P0SessionRingTrackProvider import P0SessionRingTrackProvider
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.shared.logging.Logger import Logger
from protocol0_push2.push2 import Push2
from pushbase.push_base import NUM_TRACKS, NUM_SCENES


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

    def on_select_clip_slot(self, clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        """show the clip view when selecting a clip"""
        super(P0Push2, self).on_select_clip_slot(clip_slot)
        if clip_slot.has_clip:
            ApplicationViewFacade.show_clip()
