from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # midi clip to MONO encoder
        self.add_encoder(
            identifier=4,
            name="midi clip to mono",
            on_press=lambda: SongFacade.selected_clip(MidiClip).to_mono,
        )

        # Session2ARrangement encoder
        self.add_encoder(
            identifier=16,
            name="bounce session to arrangement",
            on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement,
        )
