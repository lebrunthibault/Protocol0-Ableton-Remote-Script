from typing import Any, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.scheduler.SchedulerEvent import SchedulerEvent
from protocol0.utils.decorators import api_exposed, api_exposable_class


@api_exposable_class
class ApiRoutesManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ApiRoutesManager, self).__init__(*a, **k)
        self._midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]
        self.parent.wait(20, self._check_midi_server_is_running)  # waiting for Protocol0_midi to boot

    def _check_midi_server_is_running(self):
        # type: () -> None
        self._midi_server_check_timeout_scheduler_event = self.parent.wait(50, self._no_midi_server_found)
        self.system.ping()

    def _no_midi_server_found(self):
        # type: () -> None
        self.parent.log_warning("Midi server is not running.")

    @api_exposed
    def ping(self):
        # type: () -> None
        """ Called by the backend when the system api ping is called """
        self.parent.log_info("Midi server is running")
        if self._midi_server_check_timeout_scheduler_event:
            self._midi_server_check_timeout_scheduler_event.cancel()
        self.system.pong()  # notify midi backend that we receive well messages via Protocol0Midi

    @api_exposed
    def show_message(self, message):
        # type: (str) -> None
        self.parent.show_message(message)

    @api_exposed
    def execute_vocal_command(self, command):
        # type: (str) -> None
        """ Called by the speech recognition script """
        self.parent.vocalCommandManager.execute_command(command)
