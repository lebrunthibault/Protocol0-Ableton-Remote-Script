from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.instrument.preset.InstrumentPresetScrollerService import (
    InstrumentPresetScrollerService,
)
from protocol0.domain.lom.instrument.preset.PresetService import PresetService
from protocol0.domain.lom.sample.SampleService import SampleService
from protocol0.shared.SongFacade import SongFacade


class ActionGroupPreset(ActionGroupInterface):
    CHANNEL = 13

    def configure(self):
        # type: () -> None
        # PREset encoder
        self.add_encoder(
            identifier=1,
            name="scroll presets",
            filter_active_tracks=True,
            on_scroll=lambda: partial(
                self._container.get(InstrumentPresetScrollerService).scroll_presets_or_samples,
                SongFacade.current_track(),
            ),
        )

        # CATegory encoder
        self.add_encoder(
            identifier=2,
            name="scroll preset categories",
            on_scroll=lambda: partial(
                self._container.get(InstrumentPresetScrollerService).scroll_preset_categories,
                SongFacade.current_track(),
            ),
        )

        # CLEAn encoder
        self.add_encoder(
            identifier=13,
            name="Clean drum rack",
            on_press=self._container.get(DrumRackService).clean_racks,
        )

        # SCAN encoder
        self.add_encoder(
            identifier=15,
            active=False,
            name="Find the pitch of a drum sample",
            on_press=self._container.get(SampleService).find_out_sample_pitch,
        )

        # SCAN encoder
        self.add_encoder(
            identifier=16,
            name="scan (import) all track presets",
            on_press=self._container.get(PresetService).refresh_presets,
        )
