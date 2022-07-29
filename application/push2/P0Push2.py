from fractions import Fraction
from functools import partial

import Live
from protocol0_push2.browser_modes import BrowserModeBehaviour, AddDeviceMode, AddTrackMode
from protocol0_push2.push2 import Push2
from pushbase.push_base import NUM_TRACKS, NUM_SCENES

from ableton.v2.control_surface import Layer
from protocol0.application.push2.P0SessionRingTrackProvider import P0SessionRingTrackProvider
from protocol0.application.push2.P0ShowInstrumentMode import P0ShowInstrumentMode
from protocol0.application.push2.P0TrackListComponent import P0TrackListComponent
from protocol0.application.push2.P0TransportComponent import P0TransportComponent
from protocol0.domain.shared.utils.func import nop
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
        # switch to session view
        self._matrix_modes.selected_mode = "session"

    def _init_session_ring(self):
        # type: () -> None
        self._session_ring = P0SessionRingTrackProvider(
            name="Session_Ring", num_tracks=NUM_TRACKS, num_scenes=NUM_SCENES, is_enabled=True
        )

    def _init_browse_mode(self):
        # type: () -> None
        """Overriding this to make clicking on Browse open the instrument instead"""
        application = Live.Application.get_application()
        browser = application.browser
        self._main_modes.add_mode("browse", [P0ShowInstrumentMode(self._main_modes)])
        self._main_modes.add_mode(
            "add_device",
            [
                AddDeviceMode(
                    application=application,
                    song=self.song,
                    browser=browser,
                    drum_group_component=self._drum_component,
                    enabling_mode=self._browser_component_mode,
                )
            ],
            behaviour=BrowserModeBehaviour(),
        )
        self._main_modes.add_mode(
            "add_track",
            [AddTrackMode(browser=browser, enabling_mode=self._new_track_browser_component_mode)],
            behaviour=BrowserModeBehaviour(),
        )

    def _init_track_list(self):
        # type: () -> None
        self._track_list_component = P0TrackListComponent(
            tracks_provider=self._session_ring,
            trigger_recording_on_release_callback=self._session_recording.set_trigger_recording_on_release,
            color_chooser=self._create_color_chooser(),
            is_enabled=False,
            layer=Layer(
                track_action_buttons="select_buttons",
                lock_override_button="select_button",
                delete_button="delete_button",
                duplicate_button="duplicate_button",
                arm_button="record_button",
                select_color_button="shift_button",
            ),
        )
        self._clip_phase_enabler = self._track_list_component.clip_phase_enabler
        self._track_list_component.set_enabled(True)
        self._model.tracklistView = self._track_list_component

    # noinspection DuplicatedCode
    def _init_transport_and_recording(self):
        # type: () -> None
        """Swapping the transport class and adding shift button parameter"""
        super(P0Push2, self)._init_transport_and_recording()
        self._transport = P0TransportComponent(name="Transport")
        self._transport.layer = Layer(
            play_button="play_button",
            stop_button=self._with_shift("play_button"),
            tap_tempo_button="tap_tempo_button",
            metronome_button="metronome_button",
        )

    def _create_session(self):
        # type: () -> None
        """Swap _on_select_clip_slot"""
        # noinspection PyUnresolvedReferences
        session = super(Push2, self)._create_session()
        for scene_index in xrange(8):
            scene = session.scene(scene_index)
            for track_index in xrange(8):
                clip_slot = scene.clip_slot(track_index)
                clip_slot._do_select_clip = partial(
                    self._on_select_clip_slot, scene_index, track_index
                )
                # don't highlight when we play the clip
                clip_slot._show_launched_clip_as_highlighted_clip = nop

        return session

    def on_select_scene(self, scene):
        # type: (Live.Scene.Scene) -> None
        """unfold scene on select"""
        super(P0Push2, self).on_select_scene(scene)
        SongFacade.selected_scene().unfold()

    def _on_select_clip_slot(self, scene_index, track_index, _):
        # type: (int, int, Live.ClipSlot.ClipSlot) -> None
        """When clicking on select + clip pad"""
        track_index += self._session_ring.track_offset
        tracks = self._session_ring.session_tracks

        if track_index >= len(tracks):
            return None
        track = tracks[track_index]

        scene_index += self._session_ring.scene_offset
        if scene_index >= len(track.clip_slots):
            return None
        track.select_clip_slot(track.clip_slots[scene_index]._clip_slot)
        SongFacade.selected_clip().show_loop()
