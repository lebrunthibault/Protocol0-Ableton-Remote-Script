from typing import Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.vocal_command.KeywordActionManager import KeywordActionManager
from protocol0.enums.vocal_command.ActionEnum import ActionEnum
from protocol0.enums.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.utils.utils import smart_string


class VocalCommandManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(VocalCommandManager, self).__init__(*a, **k)
        self._keywordActionManager = KeywordActionManager()

    def execute_command(self, command):
        # type: (str) -> None
        """ Called by the speech recognition script """
        command = smart_string(command)
        self.parent.show_message(command)
        action_enum = getattr(ActionEnum, command, None)  # type: ActionEnum
        if action_enum:
            self._keywordActionManager.execute_from_enum(action_enum=action_enum)
            return

        track_search_keyword_enum = getattr(TrackSearchKeywordEnum, command, None)  # type: TrackSearchKeywordEnum
        if track_search_keyword_enum:
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        self.parent.log_error("Couldn't find matching command for input %s" % command)
