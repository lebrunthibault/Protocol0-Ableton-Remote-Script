from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.device.DrumRackSampleService import DrumRackSampleService


class ActionGroupLog(ActionGroupInterface):
    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # LOG encoder
        self.add_encoder(
            identifier=1,
            name="warp selected pad",
            on_press=self._container.get(DrumRackSampleService).warp_selected_sample,
            on_long_press=self._container.get(DrumRackSampleService).warp_all,
        )
