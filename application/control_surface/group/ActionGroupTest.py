from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.SetProfilingService import SetProfilingService

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupInterface):
    # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere

    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(identifier=1, name="test",
                         on_press=self.action_test,
                         )

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling",
                         on_press=self._container.get(SetProfilingService).profile_set)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

        # DUPLication encoder
        self.add_encoder(identifier=4, name="test server duplication",
                         on_press=Backend.client().test_duplication)

    def action_test(self):
        # type: () -> None
        pass
