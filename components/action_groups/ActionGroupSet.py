from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.devices.InstrumentProphet import InstrumentProphet
from protocol0.interface.InterfaceState import InterfaceState


class ActionGroupSet(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=3, *a, **k)
        # PUSH encoder
        # self.add_encoder(identifier=1, name="connect push2", on_press=self.parent.push2Manager.connect_push2)

        # SPLiT encoder
        self.add_encoder(identifier=1,
                         name="split scene",
                         on_scroll=InterfaceState.scroll_duplicate_scene_bar_lengths,
                         on_press=lambda: self.song.selected_scene.split
                         )

        # TAP tempo encoder
        self.add_encoder(identifier=2, name="tap tempo",
                         on_press=self.song.tap_tempo,
                         on_scroll=self.parent.songManager.scroll_tempo
                         )

        # STATs encoder
        self.add_encoder(identifier=4, name="display song stats",
                         on_press=self.parent.songStatsManager.display_song_stats)

        # REV2 encoder
        self.add_encoder(identifier=5, name="rev2 toggle vst editor",
                         on_press=InstrumentProphet.toggle_editor_plugin_on)

        # VELO encoder
        self.add_encoder(identifier=13, name="smooth selected clip velocities",
                         on_scroll=self.parent.clipManager.smooth_selected_clip_velocities)

        # FIX encoder
        self.add_encoder(identifier=14, name="scroll all tracks volume",
                         on_scroll=self.parent.mixingManager.scroll_all_tracks_volume)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self.parent.sessionToArrangementManager.bounce_session_to_arrangement)
