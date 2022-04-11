from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupMixin):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # TAP tempo encoder
        self.add_encoder(identifier=1, name="tap tempo",
                         on_press=self._song.tap_tempo,
                         on_scroll=self._song.scroll_tempo
                         )

        # VELO encoder
        self.add_encoder(identifier=13, name="smooth selected clip velocities",
                         on_scroll=lambda: SongFacade.selected_midi_clip().scale_velocities)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement)