from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupFix(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupFix, self).__init__(channel=5, *a, **k)
        # SET encoder
        self.add_encoder(identifier=1, name="refresh set appearance",
                         on_press=self.parent.setFixerManager.fix)

        # TRaCK encoder
        self.add_encoder(identifier=2, name="fix current track",
                         filter_active_tracks=True,
                         on_press=lambda: self.parent.validatorManager.fix_object(self.song.current_track))

        # DEVice encoder
        self.add_encoder(identifier=3, name="Delete unnecessary devices",
                         on_press=self.parent.setUpgradeManager.delete_unnecessary_devices)

        # CLR encoder
        self.add_encoder(identifier=4, name="clear logs", on_press=self.parent.logManager.clear)
