from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.shared.SongDataManagerInterface import SongDataManagerInterface


class ActionGroupData(ActionGroupMixin):
    CHANNEL = 7

    def configure(self):
        # type: () -> None
        # SAVE encoder
        self.add_encoder(identifier=1, name="save song data", on_press=self._container.get(SongDataManagerInterface).save)

        # CLeaR encoder
        self.add_encoder(identifier=2, name="clear song data", on_press=self._container.get(SongDataManagerInterface).clear)
