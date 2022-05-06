from fractions import Fraction
from functools import partial

import Live
from protocol0_push2.push2 import Push2
from pushbase.push_base import NUM_TRACKS, NUM_SCENES

from protocol0.application.push2.P0SessionNavigationComponent import P0SessionNavigationComponent
from protocol0.application.push2.P0SessionRingTrackProvider import P0SessionRingTrackProvider
from protocol0.domain.shared.utils import nop
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

    def _create_session(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        session = super(Push2, self)._create_session()
        for scene_index in xrange(8):
            scene = session.scene(scene_index)
            for track_index in xrange(8):
                clip_slot = scene.clip_slot(track_index)
                clip_slot._do_select_clip = partial(self._on_select_clip_slot, track_index)
                # don't highlight when we play the clip
                clip_slot._show_launched_clip_as_highlighted_clip = nop

        return session

    def _on_select_clip_slot(self, track_index, clip_slot):
        # type: (int, Live.ClipSlot.ClipSlot) -> None
        """show the clip view when selecting a clip"""
        track = SongFacade.selected_scene().abstract_tracks[track_index]
        track.select_clip_slot(clip_slot)
