from functools import partial

from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import \
    PresetProgramSelectedEvent
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerGroupTrackName import (
    PresetInitializerGroupTrackName,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentMinitaur(InstrumentInterface):
    NAME = "Minitaur"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = InstrumentColorEnum.MINITAUR
    CAN_BE_SHOWN = False
    PRESETS_PATH = (
        "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    )
    PRESET_OFFSET = 1
    HAS_PROTECTED_MODE = False
    PRESET_INITIALIZER = PresetInitializerGroupTrackName

    def set_default_preset(self):
        # type: () -> None
        DomainEventBus.emit(PresetProgramSelectedEvent(2))

    @classmethod
    def load_instrument_track(cls):
        # type: () -> Sequence
        minitaur_track = next(SongFacade.external_synth_tracks(InstrumentMinitaur), None)

        track_to_focus = minitaur_track or list(SongFacade.simple_tracks())[-1]
        track_color = track_to_focus.color

        track_to_focus.focus()
        seq = Sequence()
        seq.add(Backend.client().load_instrument_track)
        seq.wait_for_backend_event("instrument_loaded")
        seq.add(partial(setattr, track_to_focus, "color", track_color))
        return seq.done()