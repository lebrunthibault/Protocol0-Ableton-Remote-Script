from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.shared.Song import Song


class ActionGroupFix(ActionGroupInterface):
    CHANNEL = 5

    def configure(self):
        # type: () -> None
        # SET encoder
        self.add_encoder(
            identifier=1,
            name="fix set",
            on_press=self._container.get(SetFixerService).fix_set,
        )

        # TRaCK encoder
        self.add_encoder(
            identifier=2,
            name="fix current track",
            filter_active_tracks=True,
            on_press=lambda: self._container.get(ValidatorService).fix_object(
                Song.current_track()
            ),
        )
