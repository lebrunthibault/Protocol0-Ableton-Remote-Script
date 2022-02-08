from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.command.ClearLogsCommand import ClearLogsCommand
from protocol0.domain.shared.CommandBus import CommandBus
from protocol0.domain.shared.System import System
from protocol0.shared.Logger import Logger


class ActionGroupTest(ActionGroupMixin):
    """ Just a playground to launch test actions """

    CHANNEL = 16

    # channel is not 1 because 1 is reserved for non script midi
    # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(identifier=1, name="test",
                         on_press=self.action_test,
                         on_long_press=self.action_test,
                         )

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling", on_press=System.client().start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

    def action_test(self):
        # type: () -> None
        CommandBus.dispatch(ClearLogsCommand())
