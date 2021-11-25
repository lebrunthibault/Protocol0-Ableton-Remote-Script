from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupFix(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupFix, self).__init__(channel=5, filter_active_tracks=True, *a, **k)
        # SET encoder
        self.add_encoder(identifier=1, name="refresh set appearance",
                         on_press=self.parent.setFixerManager.refresh_set_appearance)

        # EXTernalSynthTrack encoder
        self.add_encoder(identifier=2, name="fix current ExternalSynthTrack",
                         on_press=lambda: self.parent.validatorManager.fix_object(self.song.current_track))

        # RACK encoder
        self.add_encoder(identifier=3, name="update rack devices",
                         on_press=self.parent.setFixerManager.update_audio_effect_racks)
