from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupMixin):
    # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere

    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(identifier=1, name="test",
                         on_press=self.action_test,
                         on_long_press=self.action_test,
                         )

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling",
                         on_press=Backend.client().start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

    def action_test(self):
        # type: () -> None
        Backend.client().move_to(1000, 1000)
        return
        clip = SongFacade.selected_midi_clip()
        parameters_couple = clip.get_linked_parameters()
        Logger.log_dev(parameters_couple)
        self._song.draw_mode = False
        for couple in parameters_couple[:1]:
            couple.link_clip_automation(clip)
