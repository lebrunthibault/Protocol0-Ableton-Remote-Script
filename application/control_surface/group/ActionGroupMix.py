from protocol0.application.control_surface.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.set.MixingService import MixingService


class ActionGroupMix(ActionGroupMixin):
    CHANNEL = 14

    def configure(self):
        # type: () -> None
        # CHecK encoder
        self.add_encoder(identifier=1, name="check clipping tracks",
                         on_press=self._container.get(MixingService).toggle_volume_check)
