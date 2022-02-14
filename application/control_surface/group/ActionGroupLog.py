from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.audit.LogService import LogService
from protocol0.shared.logging.Logger import Logger


class ActionGroupLog(ActionGroupMixin):
    CHANNEL = 9

    def configure(self):
        # type: () -> None
        # LOG encoder
        self.add_encoder(identifier=1, name="log current", on_press=self._container.get(LogService).log_current)

        # LOGS encoder
        self.add_encoder(identifier=2, name="log set", on_press=self._container.get(LogService).log_set)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)
