from fractions import Fraction
from functools import partial

import Live
from ableton.v2.control_surface import Layer
from protocol0_push2.push2 import Push2
from pushbase.push_base import NUM_TRACKS, NUM_SCENES

from protocol0.application.push2.P0SessionRingTrackProvider import P0SessionRingTrackProvider
from protocol0.application.push2.P0TrackListComponent import P0TrackListComponent
from protocol0.domain.shared.utils import nop
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class P0Push2(Push2):
    """
        Overriding Push2 by inheritance

        The only push2 modification is done in __init__.py and swaps the Push2 class
        for this one.

        This is used to modify the way the session works (using only scene tracks)
        and adding some behavior to a few buttons (track selection, clip selection)
    """
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

    def _init_track_list(self):
        # type: () -> None
        self._track_list_component = P0TrackListComponent(tracks_provider=self._session_ring,
                                                          trigger_recording_on_release_callback=self._session_recording.set_trigger_recording_on_release,
                                                          color_chooser=self._create_color_chooser(), is_enabled=False,
                                                          layer=Layer(track_action_buttons=u'select_buttons',
                                                                      lock_override_button=u'select_button',
                                                                      delete_button=u'delete_button',
                                                                      duplicate_button=u'duplicate_button',
                                                                      arm_button=u'record_button',
                                                                      select_color_button=u'shift_button'))
        self._clip_phase_enabler = self._track_list_component.clip_phase_enabler
        self._track_list_component.set_enabled(True)
        self._model.tracklistView = self._track_list_component

    def _create_session(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        session = super(Push2, self)._create_session()
        for scene_index in xrange(8):
            scene = session.scene(scene_index)
            for track_index in xrange(8):
                clip_slot = scene.clip_slot(track_index)
                clip_slot._do_select_clip = partial(self._on_select_clip_slot, scene_index, track_index)
                # don't highlight when we play the clip
                clip_slot._show_launched_clip_as_highlighted_clip = nop

        return session

    def _on_select_clip_slot(self, scene_index, track_index, _):
        # type: (int, int, Live.ClipSlot.ClipSlot) -> None
        """When clicking on select + clip pad"""
        track_index += self._session_ring.track_offset
        if track_index >= len(SongFacade.selected_scene().abstract_tracks):
            return None
        track = SongFacade.selected_scene().abstract_tracks[track_index]

        scene_index += self._session_ring.scene_offset
        if scene_index >= len(track.clip_slots):
            return None
        track.select_clip_slot(track.clip_slots[scene_index]._clip_slot)
        SongFacade.selected_clip().show_loop()
