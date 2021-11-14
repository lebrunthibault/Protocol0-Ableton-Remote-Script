from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.PixelEnum import PixelEnum


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=1, *a, **k)
        # TEST encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)
        # RELOad time encoder
        self.add_encoder(identifier=2, name="profile set reload time", on_press=self.start_set_profiling)

    def action_test(self):
        # type: () -> None
        self.system.double_click(*PixelEnum.FOLD_CLIP_NOTES.coordinates)

    def start_set_profiling(self):
        # type: () -> None
        self.system.start_set_profiling()
