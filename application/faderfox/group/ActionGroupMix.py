from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin


class ActionGroupMix(ActionGroupMixin):
    CHANNEL = 6

    def configure(self):
        # type: () -> None
        # CHecK encoder
        self.add_encoder(identifier=1, name="check clipping tracks",
                         on_press=self._container.mixing_manager.toggle_volume_check)
