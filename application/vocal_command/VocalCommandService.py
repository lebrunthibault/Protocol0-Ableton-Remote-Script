from typing import cast, Optional

from protocol0.application.vocal_command.KeywordSearchService import KeywordSearchService
from protocol0.application.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.application.vocal_command.VocalActionEnum import VocalActionEnum
from protocol0.application.CommandBus import CommandBus
from protocol0.domain.shared.utils import smart_string
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar


class VocalCommandService(object):
    def __init__(self, keyword_search_service):
        # type: (KeywordSearchService) -> None
        self._keyword_search_service = keyword_search_service

    def execute_command(self, command):
        # type: (str) -> None
        """ Called by the speech recognition script """
        command = smart_string(command)
        StatusBar.show_message(command)
        action_enum = cast(Optional[VocalActionEnum], getattr(VocalActionEnum, command, None))
        if action_enum:
            CommandBus.dispatch(action_enum.value())
            return

        track_search_keyword_enum = cast(Optional[TrackSearchKeywordEnum], getattr(TrackSearchKeywordEnum, command, None))
        if track_search_keyword_enum:
            self._keyword_search_service.search_track(keyword_enum=track_search_keyword_enum)
            return

        Logger.log_error("Couldn't find matching command for input %s" % command)
