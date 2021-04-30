from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup


class ActionGroupSet(AbstractActionGroup):
    """
    This manager is supposed to group mundane tasks on Live like debug
    or one shot actions on a set (like upgrading to a new naming scheme)
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupSet, self).__init__(channel=14, filter_active_tracks=False, *a, **k)
        # LOG encoder
        self.add_encoder(id=1, name="log", on_press=self.parent.logManager.log_set)

        # 2. empty

        # CHeCK encoder
        self.add_encoder(id=3, name="check", on_press=self.parent.setFixerManager.check_set)

        # FIX encoder
        self.add_encoder(id=4, name="fix", on_press=self.parent.setFixerManager.refresh_set_appearance)
