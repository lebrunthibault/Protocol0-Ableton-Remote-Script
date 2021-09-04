from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.FastScheduler import SchedulerEvent
from protocol0.components.vocal_command.KeywordActionManager import KeywordActionManager
from protocol0.enums.vocal_command.ActionEnum import ActionEnum
from protocol0.enums.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.utils.decorators import api_exposed, api_exposable_class
from typing import Any, Optional

from protocol0.utils.utils import smart_string


@api_exposable_class
class VocalCommandManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(VocalCommandManager, self).__init__(*a, **k)
        self._keywordActionManager = KeywordActionManager()
        self._midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]
        self._check_midi_server_is_running()

    def _check_midi_server_is_running(self):
        def no_server_found():
            self.parent.log_error("Midi server is not running.")
        self._midi_server_check_timeout_scheduler_event = self.parent.wait(100, no_server_found)
        self.system.ping()

    @api_exposed
    def ping(self):
        # type: () -> None
        self.parent.log_info("test API called successful")
        self._midi_server_check_timeout_scheduler_event.cancel()

    @api_exposed
    def execute_command(self, command):
        # type: (str) -> None
        command = smart_string(command)
        command_enum = getattr(ActionEnum, command, None)
        if command_enum:
            self.parent.show_message(command)
            self.parent.show_message("SR received action")
            return

        track_search_keyword_enum = getattr(TrackSearchKeywordEnum, command, None)
        if track_search_keyword_enum:
            self.parent.show_message("SR received search")
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        self.parent.log_error("Couldn't find matching command for input %s" % command)
