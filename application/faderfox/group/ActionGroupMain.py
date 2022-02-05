from functools import partial

from typing import Any

from protocol0.application.faderfox.group.AbstractActionGroup import AbstractActionGroup
from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.application.faderfox.InterfaceState import InterfaceState


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMain, self).__init__(channel=4, *a, **k)

        # TAIL encoder
        self.add_encoder(
            identifier=2,
            name="toggle audio clip tail recording",
            filter_active_tracks=True,
            on_press=lambda: self.song.current_external_synth_track.toggle_record_clip_tails,
        )

        # AUTOmation encoder
        self.add_encoder(
            identifier=3,
            name="automation",
            on_press=lambda: self.parent.automationTrackManager.display_selected_parameter_automation(self.song.selected_clip),
            on_scroll=self.parent.automationTrackManager.scroll_automation_envelopes,
        )

        # VOLume tempo encoder
        self.add_encoder(identifier=4, name="volume",
                         filter_active_tracks=True,
                         on_scroll=lambda: self.song.current_track.scroll_volume
                         )

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            filter_active_tracks=True,
            on_press=lambda: self.song.current_external_synth_track.monitoring_state.switch)

        # RECord encoder
        self.add_encoder(
            identifier=9,
            name="record",
            filter_active_tracks=True,
            on_scroll=InterfaceState.scroll_recording_time,
            on_press=lambda: partial(self.parent.trackRecorderManager.record_track, self.song.current_track,
                                     RecordTypeEnum.NORMAL),
            on_cancel_press=lambda: partial(self.parent.trackRecorderManager.cancel_record, self.song.current_track,
                                            RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.parent.trackRecorderManager.record_track, self.song.current_track,
                                          RecordTypeEnum.AUDIO_ONLY),
            on_cancel_long_press=lambda: partial(self.parent.trackRecorderManager.cancel_record,
                                                 self.song.current_track,
                                                 RecordTypeEnum.AUDIO_ONLY)
        )

        # SCENe 2 encoder
        self.add_encoder(
            identifier=12,
            name="scene scroll time",
            on_scroll=lambda: self.song.selected_scene.scroll_position,
            on_press=lambda: self.song.last_manually_started_scene.fire_and_move_position,
            on_long_press=lambda: self.song.current_track.toggle_fold,
        )

        # TRacK encoder
        self.add_encoder(
            identifier=13,
            name="track",
            on_scroll=self.song.scroll_tracks,
            on_press=lambda: self.song.current_track.toggle_arm,
            on_long_press=lambda: self.song.current_track.toggle_fold,
        )

        # INSTrument encoder
        self.add_encoder(
            identifier=14,
            name="instrument",
            filter_active_tracks=True,
            on_press=self.parent.instrumentDisplayManager.show_hide_instrument,
            on_long_press=self.parent.instrumentDisplayManager.activate_instrument_plugin_window,
            on_scroll=lambda: partial(self.parent.instrumentPresetScrollerManager.scroll_presets_or_samples, self.song.current_track.instrument),
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.fire,
            on_long_press=lambda: self.song.selected_scene.toggle_loop,
            on_scroll=self.song.scroll_scenes,
        )
