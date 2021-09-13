from typing import Any, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.FastScheduler import SchedulerEvent
from protocol0.components.vocal_command.KeywordActionManager import KeywordActionManager
from protocol0.enums.vocal_command.ActionEnum import ActionEnum
from protocol0.enums.vocal_command.TrackSearchKeywordEnum import TrackSearchKeywordEnum
from protocol0.utils.decorators import api_exposed, api_exposable_class
from protocol0.utils.utils import smart_string


@api_exposable_class
class VocalCommandManager(AbstractControlSurfaceComponent):
    MIDI_SERVER_RUNNING = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(VocalCommandManager, self).__init__(*a, **k)
        self._keywordActionManager = KeywordActionManager()
        self._midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]
        self.parent.wait(20, self._check_midi_server_is_running)  # waiting for Protocol0_midi to boot

    def _check_midi_server_is_running(self):
        # type: () -> None
        self.parent.log_debug("checking midi server")
        self._midi_server_check_timeout_scheduler_event = self.parent.wait(50, self._no_midi_server_found)
        self.parent.log_debug(
            "self._midi_server_check_timeout_scheduler_event: %s" % self._midi_server_check_timeout_scheduler_event)
        self.system.ping()

    def _no_midi_server_found(self):
        # type: () -> None
        if not self.MIDI_SERVER_RUNNING:
            self.parent.log_error("Midi server is not running.")

    @api_exposed
    def ping(self):
        # type: () -> None
        """ Called by the backend when the system api ping is called """
        self.parent.log_info("Midi server is running")
        if self._midi_server_check_timeout_scheduler_event:
            self._midi_server_check_timeout_scheduler_event.cancel()
        self.MIDI_SERVER_RUNNING = True
        self.system.pong()  # notify midi backend that we receive well messages via Protocol0Midi

    @api_exposed
    def execute_command(self, command):
        # type: (str) -> None
        """ Called by the speech recognition script """
        command = smart_string(command)
        action_enum = getattr(ActionEnum, command, None)  # type: ActionEnum
        if action_enum:
            self.parent.show_message("SR received action: %s" % action_enum.value)
            self._keywordActionManager.execute_from_enum(action_enum=action_enum)
            return

        track_search_keyword_enum = getattr(TrackSearchKeywordEnum, command, None)  # type: TrackSearchKeywordEnum
        if track_search_keyword_enum:
            self.parent.show_message("SR received search: %s" % track_search_keyword_enum.value)
            self.parent.keywordSearchManager.search_track(keyword_enum=track_search_keyword_enum)
            return

        self.parent.log_error("Couldn't find matching command for input %s" % command)
