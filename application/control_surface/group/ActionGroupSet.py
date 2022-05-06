from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # TAP tempo encoder
        self.add_encoder(identifier=1, name="tap tempo",
                         on_press=self._container.get(TempoComponent).tap,
                         on_scroll=self._container.get(TempoComponent).scroll
                         )

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement)
