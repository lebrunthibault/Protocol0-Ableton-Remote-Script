from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.config import Config
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum


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
        self.parent.setFixerManager.link_external_synth_track_dummy_tracks(self.song.current_track)
        # self.parent.setFixerManager.delete_all_unmodified_lfo_tool()

    def start_set_profiling(self):
        # type: () -> None
        if Config.ABLETON_SESSION_TYPE != AbletonSessionTypeEnum.PROFILING:
            self.parent.show_message("set the config to profiling")
            return
        self.system.start_set_profiling()
