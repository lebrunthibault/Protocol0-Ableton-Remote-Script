from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.ActionEnum import ActionEnum
from protocol0.enums.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.utils.decorators import api_exposed, api_exposable_class
from protocol0.utils.log import log_ableton


@api_exposable_class
class VocalCommandManager(AbstractControlSurfaceComponent):
    @api_exposed
    def test(self):
        # type: () -> None
        log_ableton("test API called successful")

    @api_exposed
    def execute_command(self, command):
        # type: (str) -> None
        command_enum = ActionEnum.get_from_value(command)
        self.parent.log_info("Got %s" % command_enum)
        if command_enum:
            self.parent.vocalCommandManager.execute_from_enum(command=command_enum)
            return

        track_search_keyword_enum = TrackSearchKeywordEnum.get_from_value(command)
        if track_search_keyword_enum:
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        self.parent.log_error("Couldn't find matching command for input %s" % command)
