from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin


class ActionGroupData(ActionGroupMixin):
    CHANNEL = 7

    def configure(self):
        # type: () -> None
        # SAVE encoder
        self.add_encoder(identifier=1, name="save song data", on_press=self._container.song_data_manager.save)

        # CLeaR encoder
        self.add_encoder(identifier=2, name="clear song data", on_press=self._container.song_data_manager.clear)
