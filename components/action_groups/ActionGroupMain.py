from functools import partial

from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState


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
            on_scroll=lambda: self.song.current_external_synth_track.scroll_record_clip_tails,
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
            on_press=lambda: self.song.current_track.switch_monitoring)

        # RECord encoder
        self.add_encoder(
            identifier=9,
            name="record",
            filter_active_tracks=True,
            on_scroll=InterfaceState.scroll_recording_time,
            on_press=lambda: partial(self.parent.trackRecorderManager.record_track, self.song.current_track,
                                     RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.parent.trackRecorderManager.record_track, self.song.current_track,
                                          RecordTypeEnum.AUDIO_ONLY)
        )

        # SCENe 2 encoder
        self.add_encoder(
            identifier=12,
            name="scene scroll time",
            on_press=lambda: self.song.last_manually_started_scene.fire_and_move_position,
            on_scroll=lambda: self.song.selected_scene.scroll_position,
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
            on_press=lambda: self.song.current_track.show_hide_instrument,
            on_long_press=lambda: self.song.current_track.activate_instrument_plugin_window,
            on_scroll=lambda: self.song.current_track.scroll_presets_or_samples,
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.fire,
            on_long_press=lambda: self.song.selected_scene.toggle_loop,
            on_scroll=self.song.scroll_scenes,
        )
