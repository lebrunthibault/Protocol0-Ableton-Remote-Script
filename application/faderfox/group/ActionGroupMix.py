from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.set.MixingManager import MixingManager


class ActionGroupMix(ActionGroupMixin):
    CHANNEL = 6

    def configure(self):
        # type: () -> None
        # CHecK encoder
        self.add_encoder(identifier=1, name="check clipping tracks",
                         on_press=self._container.get(MixingManager).toggle_volume_check)
