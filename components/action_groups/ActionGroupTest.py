from typing import Any, cast

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.config import Config
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        # channel is not 1 because 1 is reserved for non script midi
        # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere
        super(ActionGroupTest, self).__init__(channel=16, *a, **k)
        # TEST encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)
        # RELOad time encoder
        self.add_encoder(identifier=2, name="profile set reload time", on_press=self.start_set_profiling)

    def action_test(self):
        # type: () -> None
        track = cast(ExternalSynthTrack, self.song.current_track)
        track.instrument.device.toggle_off()

    def start_set_profiling(self):
        # type: () -> None
        if Config.ABLETON_SESSION_TYPE != AbletonSessionTypeEnum.PROFILING:
            self.parent.show_message("set the config to profiling")
            return
        self.system.start_set_profiling()
