from functools import partial

from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import InstrumentPresetScrollerService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.track_recorder_service import TrackRecorderService
from protocol0.shared.InterfaceState import InterfaceState
from protocol0.shared.SongFacade import SongFacade


class ActionGroupMain(ActionGroupMixin):
    """
    Main group: gathering most the functionalities. My faithful companion when producing on Live !
    """

    CHANNEL = 4

    def configure(self):
        # type: () -> None
        # AUTOmation encoder
        self.add_encoder(
            identifier=3,
            name="automation",
            on_press=lambda: SongFacade.selected_clip().display_current_parameter_automation,
            on_scroll=lambda: SongFacade.selected_clip().scroll_automation_envelopes,
        )

        # VOLume tempo encoder
        self.add_encoder(identifier=4, name="volume",
                         filter_active_tracks=True,
                         on_scroll=lambda: SongFacade.current_track().scroll_volume
                         )

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            filter_active_tracks=True,
            on_press=lambda: SongFacade.current_external_synth_track().monitoring_state.switch)

        # RECord encoder
        self.add_encoder(
            identifier=9,
            name="record",
            filter_active_tracks=True,
            on_scroll=InterfaceState.scroll_recording_time,
            on_press=lambda: partial(self._container.get(TrackRecorderService).record_track, SongFacade.current_track(),
                                     RecordTypeEnum.NORMAL),
            on_cancel_press=lambda: partial(self._container.get(TrackRecorderService).cancel_record, SongFacade.current_track(),
                                            RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self._container.get(TrackRecorderService).record_track, SongFacade.current_track(),
                                          RecordTypeEnum.AUDIO_ONLY),
            on_cancel_long_press=lambda: partial(self._container.get(TrackRecorderService).cancel_record,
                                                 SongFacade.current_track(),
                                                 RecordTypeEnum.AUDIO_ONLY)
        )

        # SCENe 2 encoder
        self.add_encoder(
            identifier=12,
            name="scene scroll time",
            on_scroll=lambda: SongFacade.selected_scene().scroll_position,
            on_press=lambda: SongFacade.last_manually_started_scene().fire_and_move_position,
            on_long_press=lambda: SongFacade.current_track().toggle_fold,
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
            on_press=self._container.get(InstrumentDisplayService).show_hide_instrument,
            on_long_press=self._container.get(InstrumentDisplayService).activate_instrument_plugin_window,
            on_scroll=lambda: partial(self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples, SongFacade.current_track().instrument),
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: SongFacade.selected_scene().fire,
            on_long_press=lambda: SongFacade.selected_scene().toggle_loop,
            on_scroll=self._song.scroll_scenes,
        )
