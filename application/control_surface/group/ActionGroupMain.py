from functools import partial

from typing import Optional

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import (
    InstrumentPresetScrollerService,
)
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.track.TrackAutomationService import TrackAutomationService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class ActionGroupMain(ActionGroupInterface):
    """
    Main group: gathering most the functionalities. My faithful companion when producing on Live !
    """

    CHANNEL = 4

    def configure(self):
        # type: () -> None
        def record_track(record_type):
            # type: (RecordTypeEnum) -> Optional[Sequence]
            return self._container.get(TrackRecorderService).record_track(
                SongFacade.current_track(), record_type
            )

        # VELO encoder
        self.add_encoder(
            identifier=2,
            name="smooth selected clip velocities",
            on_scroll=lambda: SongFacade.selected_midi_clip().scale_velocities,
        )

        # AUTOmation encoder
        self.add_encoder(
            identifier=3,
            name="automation",
            on_press=lambda: self._container.get(TrackAutomationService).show_automation,
            on_long_press=lambda: self._container.get(
                TrackAutomationService
            ).select_or_sync_automation,
            on_scroll=lambda: partial(
                SongFacade.selected_clip().automation.scroll_envelopes,
                SongFacade.selected_track().devices.parameters,
            ),
        )

        # VOLume tempo encoder
        self.add_encoder(
            identifier=4,
            name="volume",
            filter_active_tracks=True,
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            filter_active_tracks=True,
            on_press=lambda: SongFacade.current_external_synth_track().monitoring_state.switch,
        )

        # RECordAudio encoder
        self.add_encoder(
            identifier=5,
            name="record audio and keep automation",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY_AUTOMATION),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION),
        )

        # RECord normal encoder
        self.add_encoder(
            identifier=9,
            name="record normal",
            filter_active_tracks=True,
            on_scroll=self._container.get(
                TrackRecorderService
            ).recording_bar_length_scroller.scroll,
            on_press=lambda: partial(record_track, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.NORMAL_UNLIMITED),
        )

        # TRacK encoder
        self.add_encoder(
            identifier=13,
            name="track",
            on_scroll=self._container.get(TrackComponent).scroll_tracks,
            on_press=lambda: SongFacade.current_track().arm_state.toggle,
        )

        # INSTrument encoder
        self.add_encoder(
            identifier=14,
            name="instrument",
            filter_active_tracks=True,
            on_press=lambda: partial(
                self._container.get(InstrumentDisplayService).activate_instrument_plugin_window,
                SongFacade.current_track(),
            ),
            on_long_press=lambda: partial(
                self._container.get(InstrumentDisplayService).show_hide_instrument,
                SongFacade.current_track(),
            ),
            on_scroll=lambda: partial(
                self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples,
                SongFacade.current_track(),
            ),
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: SongFacade.selected_scene().fire,
            on_long_press=self._container.get(SceneComponent).looping_scene_toggler.toggle,
            on_scroll=self._container.get(SceneComponent).scroll_scenes,
        )
