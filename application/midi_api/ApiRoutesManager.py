from protocol0.application.midi_api.decorators import api_exposed, api_exposable_class
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.shared.AccessGlobalState import AccessGlobalState


@api_exposable_class
class ApiRoutesManager(AccessGlobalState):
    @api_exposed
    def ping(self):
        # type: () -> None
        """ Called by the backend when the system midi_api ping is called """
        self.parent.log_info("Midi server is running")
        if self.parent.midi_server_check_timeout_scheduler_event:
            self.parent.midi_server_check_timeout_scheduler_event.cancel()

    @api_exposed
    def show_message(self, message):
        # type: (str) -> None
        self.parent.show_message(message)

    @api_exposed
    def clear_logs(self):
        # type: () -> None
        self.parent.logManager.clear()

    @api_exposed
    def reset_song(self):
        # type: () -> None
        if not self.song:
            self.parent.log_error("You are still in profiling mode")
        else:
            self.song.reset(save_data=True)

    @api_exposed
    def execute_vocal_command(self, command):
        # type: (str) -> None
        """ Called by the speech recognition script """
        self.parent.vocalCommandManager.execute_command(command)

    @api_exposed
    def system_response(self, res):
        # type: (bool) -> None
        waiting_sequence = next((seq for seq in Sequence.RUNNING_SEQUENCES if seq.waiting_for_system), None)
        if waiting_sequence is None:
            self.parent.log_info("Response (%s) received from system but couldn't find a waiting sequence" % res)
            return

        waiting_sequence.on_system_response(res=res)
