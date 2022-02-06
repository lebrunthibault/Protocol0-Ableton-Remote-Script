from typing import Any, cast

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.application.vocal_command.KeywordActionManager import KeywordActionManager
from protocol0.application.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.application.vocal_command.VocalActionEnum import VocalActionEnum
from protocol0.domain.shared.utils import smart_string
from protocol0.shared.Logger import Logger


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
        action_enum = cast(VocalActionEnum, getattr(VocalActionEnum, command, None))
        if action_enum:
            self._keywordActionManager.execute_from_enum(action_enum=action_enum)
            return

        track_search_keyword_enum = cast(TrackSearchKeywordEnum, getattr(TrackSearchKeywordEnum, command, None))
        if track_search_keyword_enum:
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        Logger.log_error("Couldn't find matching command for input %s" % command)
