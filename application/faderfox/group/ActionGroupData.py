from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.infra.persistence.SongDataService import SongDataService


class ActionGroupData(ActionGroupMixin):
    CHANNEL = 7

    def configure(self):
        # type: () -> None
        # SAVE encoder
        self.add_encoder(identifier=1, name="save song data", on_press=self._container.get(SongDataService).save)
