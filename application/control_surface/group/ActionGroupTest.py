from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.SetProfilingService import SetProfilingService
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupInterface):
    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(
            identifier=1,
            name="test",
            on_press=self.action_test,
            on_scroll=self.action_test_scroll,
        )

        # PROFiling encoder
        self.add_encoder(
            identifier=2,
            name="start set launch time profiling",
            on_press=self._container.get(SetProfilingService).profile_set,
        )

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

        # DUPLication encoder
        self.add_encoder(
            identifier=4, name="test server duplication", on_press=Backend.client().test_duplication
        )

        # USAMo encoder
        self.add_encoder(
            identifier=13,
            name="check usamo latency",
            on_press=lambda: partial(
                self._container.get(AudioLatencyAnalyzerService).test_audio_latency,
                SongFacade.current_external_synth_track(),
            ),
        )

    def action_test(self):
        # type: () -> None
        device = list(SongFacade.selected_track().devices)[0]  # type: RackDevice
        Logger.dev(device._device.has_macro_mappings)
        Logger.dev(device._device.parameters)
        Logger.dev([p.name for p in device._device.parameters])

    def action_test_scroll(self, go_next):
        # type: (bool) -> None
        SongFacade.selected_parameter().scroll(go_next)
