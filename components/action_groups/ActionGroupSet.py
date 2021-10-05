from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.interface.InterfaceState import InterfaceState


class ActionGroupSet(AbstractActionGroup):
    """
    This manager is supposed to group mundane tasks on Live like debug
    or one shot actions on a set (like upgrading to the current naming scheme)
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=14, filter_active_tracks=False, *a, **k)
        # LOG encoder
        self.add_encoder(identifier=1, name="log current", on_press=self.parent.logManager.log_current)

        # LOGS encoder
        self.add_encoder(identifier=2, name="log set", on_press=self.parent.logManager.log_set)

        # CHeCK encoder
        self.add_encoder(identifier=3, name="check", on_press=self.parent.setFixerManager.check_set)

        # FIX encoder
        self.add_encoder(identifier=4, name="fix", on_press=self.parent.setFixerManager.refresh_set_appearance)

        # CLR encoder
        self.add_encoder(identifier=5, name="clear logs", on_press=self.parent.logManager.clear)

        # RACK encoder
        self.add_encoder(identifier=6, name="update rack devices",
                         on_press=self.parent.setFixerManager.update_audio_effect_racks)

        # ACTiVate encoder
        self.add_encoder(identifier=7, name="deactivate current instrument",
                         on_press=self.deactivate_instrument)

        # PUSH encoder
        self.add_encoder(identifier=13, name="connect push2", on_press=self.parent.push2Manager.connect_push2)

        # MIX encoder
        self.add_encoder(identifier=14, name="scroll all tracks volume", on_scroll=self.parent.trackManager.scroll_all_tracks_volume)

        # TAIL encoder
        self.add_encoder(identifier=15, name="toggle audio clip tails recording", on_press=InterfaceState.toggle_record_audio_clip_tails)

        # RECord encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement", on_press=self.song.bounce_session_to_arrangement)

    def deactivate_instrument(self):
        # type: () -> None
        self.song.current_track.instrument.activated = False
        self.parent.log_info("Manually deactivated instrument")
