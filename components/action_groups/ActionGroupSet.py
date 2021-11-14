from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.interface.InterfaceState import InterfaceState


class ActionGroupSet(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=3, *a, **k)
        # LOG encoder
        self.add_encoder(identifier=1, name="log current", on_press=self.parent.logManager.log_current)

        # LOGS encoder
        self.add_encoder(identifier=2, name="log set", on_press=self.parent.logManager.log_set)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=self.parent.logManager.clear)

        # AUTOmation encoder
        self.add_encoder(
            identifier=4,
            name="automation",
            on_press=self.parent.automationTrackManager.display_selected_parameter_automation,
            on_scroll=self.parent.automationTrackManager.scroll_automation_envelopes,
        )

        # PUSH encoder
        self.add_encoder(identifier=5, name="connect push2", on_press=self.parent.push2Manager.connect_push2)

        # SPLiT encoder
        self.add_encoder(identifier=6, name="split scene", on_press=lambda: self.song.selected_scene.split)

        # DUPScene encoder
        self.add_encoder(identifier=7, name="partial duplicate scene",
                         on_press=lambda: self.song.selected_scene.partial_duplicate,
                         on_scroll=InterfaceState.scroll_duplicate_scene_bar_lengths,
                         )

        # DATA encoder
        self.add_encoder(identifier=8, name="clear song data", on_press=self.parent.songDataManager.clear_data)

        # MIX encoder
        self.add_encoder(identifier=13, name="scroll all tracks volume",
                         on_scroll=self.parent.trackManager.scroll_all_tracks_volume)

        # VELO encoder
        self.add_encoder(identifier=14, name="scale selected clip velocities",
                         on_scroll=self.parent.clipManager.scale_selected_clip_velocities)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self.song.bounce_session_to_arrangement)
