from functools import partial

from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.track.AbstractTrackList import AbstractTrackList


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMain, self).__init__(channel=4, filter_active_tracks=True, *a, **k)

        # AUTOmation encoder
        self.add_encoder(
            identifier=1,
            name="automation",
            on_press=self.parent.automationTrackManager.display_selected_parameter_automation,
            on_scroll=self.parent.automationTrackManager.scroll_automation_envelopes,
        )

        # TAIL encoder
        self.add_encoder(
            identifier=2,
            name="toggle audio clip tails recording",
            on_press=InterfaceState.toggle_record_clip_tails,
            on_scroll=InterfaceState.scroll_clip_tails_bar_lengths,
        )

        # LOCK encoder
        self.add_encoder(identifier=3, name="protected mode", on_press=InterfaceState.toggle_protected_mode)

        # SPLiT encoder
        self.add_encoder(identifier=4, name="split scene", on_press=lambda: self.song.selected_scene.split)

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            on_press=lambda: AbstractTrackList(self.song.armed_tracks, self.song.selected_abstract_tracks).switch_monitoring)

        # RECord encoder
        self.add_encoder(
            identifier=9,
            name="record",
            on_scroll=InterfaceState.scroll_recording_time,
            on_press=lambda: partial(self.song.armed_tracks.record, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.song.armed_tracks.record, RecordTypeEnum.AUDIO_ONLY)
        )

        # TRaCK encoder
        self.add_encoder(
            identifier=13,
            name="track",
            on_scroll=self.song.scroll_tracks,
            on_press=lambda: self.song.current_track.toggle_arm,
            on_long_press=lambda: self.song.current_track.toggle_solo,
        )

        # INSTrument encoder
        self.add_encoder(
            identifier=14,
            name="instrument",
            on_press=lambda: self.song.current_track.show_hide_instrument,
            on_long_press=lambda: self.song.current_track.activate_instrument_plugin_window,
            on_scroll=lambda: self.song.current_track.scroll_presets_or_samples,
        )

        # CATegory encoder
        self.add_encoder(
            identifier=15, name="track category", on_scroll=lambda: self.song.current_track.scroll_preset_categories
        )

        # SCENe encoder
        self.add_encoder(
            identifier=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.fire,
            on_long_press=lambda: self.song.selected_scene.toggle_solo,
            on_scroll=self.song.scroll_scenes,
        )
