from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
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
                         on_press=Backend.client().start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

    def action_test(self):
        # type: () -> None
        track = SongFacade.selected_track()
        clip = track.clips[0]
        parameter = clip.automation.get_automated_parameters(track.devices.parameters)[0]
        envelope = clip.automation.get_envelope(parameter)
        Logger.dev(envelope)
        Logger.dev(envelope.value_at_time(0))

        envelope.insert_step(2, 1, 135)
