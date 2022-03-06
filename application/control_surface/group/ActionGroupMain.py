from functools import partial

from typing import Optional

from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import InstrumentPresetScrollerService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class ActionGroupMain(ActionGroupMixin):
    """
    Main group: gathering most the functionalities. My faithful companion when producing on Live !
    """

    CHANNEL = 4

    def configure(self):
        # type: () -> None
        def record_track(record_type):
            # type: (RecordTypeEnum) -> Optional[Sequence]
            return self._container.get(TrackRecorderService).record_track(SongFacade.current_track(), record_type)

        # RECO encoder
        self.add_encoder(
            identifier=1,
            name="record audio and keep automation",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY_AUTOMATION),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY_MULTI_AUTOMATION),
        )

        # AUTOmation encoder
        self.add_encoder(
            identifier=3,
            name="automation",
            on_press=lambda: SongFacade.selected_clip().display_current_parameter_automation,
            on_long_press=lambda: SongFacade.selected_midi_clip().synchronize_automation_layers,
            on_scroll=lambda: SongFacade.selected_clip().scroll_automation_envelopes,
        )

        # VOLume tempo encoder
        self.add_encoder(identifier=4, name="volume",
                         filter_active_tracks=True,
                         on_scroll=self._container.get(MixingService).scroll_all_tracks_volume
                         )

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            filter_active_tracks=True,
            on_press=lambda: SongFacade.current_external_synth_track().monitoring_state.switch)

        # RECordAudio encoder
        self.add_encoder(
            identifier=5,
            name="record audio",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_ONLY_MULTI),
        )

        # RECord normal encoder
        self.add_encoder(
            identifier=9,
            name="record normal",
            filter_active_tracks=True,
            on_scroll=self._container.get(TrackRecorderService).recording_bar_length_scroller.scroll,
            on_press=lambda: partial(record_track, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.NORMAL_UNLIMITED),
        )

        # SCENe 2 encoder
        self.add_encoder(
            identifier=12,
            name="scene scroll time",
            on_scroll=lambda: SongFacade.selected_scene().position_scroller.scroll,
            on_press=lambda: SongFacade.last_manually_started_scene().fire_to_position,
        )

        # TRacK encoder
        self.add_encoder(
            identifier=13,
            name="track",
            on_scroll=self._song.scroll_tracks,
            on_press=lambda: SongFacade.current_track().toggle_arm,
            on_long_press=lambda: SongFacade.current_track().toggle_fold,
        )

        # INSTrument encoder
        self.add_encoder(
            identifier=14,
            name="instrument",
            filter_active_tracks=True,
            on_press=lambda: partial(self._container.get(InstrumentDisplayService).show_hide_instrument, SongFacade.current_instrument()),
            on_long_press=lambda: partial(self._container.get(InstrumentDisplayService).activate_instrument_plugin_window, SongFacade.current_instrument()),
            on_scroll=lambda: partial(self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples, SongFacade.current_instrument()),
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: SongFacade.selected_scene().fire,
            on_long_press=self._song.looping_scene_toggler.toggle,
            on_scroll=self._song.scroll_scenes,
        )
