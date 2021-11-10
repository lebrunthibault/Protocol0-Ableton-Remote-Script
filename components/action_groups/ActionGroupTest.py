import time

from typing import Any, Optional

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.enums.DeviceEnum import DeviceEnum


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=1, *a, **k)
        # TEST encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)
        # RELOad time encoder
        self.add_encoder(identifier=2, name="set reload time", on_press=self.store_reload_time)

        self.parent.log_dev("toto")

    def action_test(self):
        # type: () -> None
        self.song.selected_track.load_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT)

    def store_reload_time(self):
        # type: () -> None
        self.system.store_ableton_set_reloaded_at()
        self.system.reload_ableton()

