from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.interface.InterfaceState import InterfaceState


class ActionGroupSet(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=3, *a, **k)
        # PUSH encoder
        # self.add_encoder(identifier=1, name="connect push2", on_press=self.parent.push2Manager.connect_push2)

        # SPLiT encoder
        self.add_encoder(identifier=2, name="split scene", on_press=lambda: self.song.selected_scene.split)

        # DUPScene encoder
        self.add_encoder(identifier=3, name="partial duplicate scene",
                         on_press=lambda: self.song.selected_scene.partial_duplicate,
                         on_scroll=InterfaceState.scroll_duplicate_scene_bar_lengths,
                         )

        # DATA encoder
        self.add_encoder(identifier=4, name="clear song data", on_press=self.parent.songDataManager.clear_data)

        # VELO encoder
        self.add_encoder(identifier=14, name="scale selected clip velocities",
                         on_scroll=self.parent.clipManager.scale_selected_clip_velocities)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self.song.bounce_session_to_arrangement)
