from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.vocal_command.KeywordActionManager import KeywordActionManager
from protocol0.enums.vocal_command.ActionEnum import ActionEnum
from protocol0.enums.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.utils.decorators import api_exposed, api_exposable_class
from protocol0.utils.log import log_ableton
from typing import Any

from protocol0.utils.utils import smart_string


@api_exposable_class
class VocalCommandManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(VocalCommandManager, self).__init__(*a, **k)
        self._keywordActionManager = KeywordActionManager()

    @api_exposed
    def test(self):
        # type: () -> None
        log_ableton("test API called successful")

    @api_exposed
    def execute_command(self, command):
        # type: (str) -> None
        command = smart_string(command)
        command_enum = getattr(ActionEnum, command, None)
        if command_enum:
            self.parent.show_message("SR received action %s" % command)
            self._keywordActionManager.execute_from_enum(command=command_enum)
            return

        track_search_keyword_enum = getattr(TrackSearchKeywordEnum, command, None)
        if track_search_keyword_enum:
            self.parent.show_message("SR received search %s" % command)
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        self.parent.log_error("Couldn't find matching command for input %s" % command)
