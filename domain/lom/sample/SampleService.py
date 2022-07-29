from functools import partial

from typing import cast

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import InstrumentSimpler
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SampleService(object):
    def __init__(self, browser_service, device_component):
        # type: (BrowserServiceInterface, DeviceComponent) -> None
        self._browser_service = browser_service
        self._device_component = device_component

    def find_out_sample_pitch(self):
        # type: () -> Sequence
        instrument = SongFacade.selected_track().instrument
        if type(instrument) not in (InstrumentSimpler, InstrumentDrumRack):
            raise Protocol0Warning("Expected a drum rack or a simpler")

        seq = Sequence()
        seq.add(partial(self._browser_service.load_device_from_enum, DeviceEnum.SAMPLE_PITCH_RACK))
        seq.wait_ms(1000)
        seq.add(self._find_out_sample_pitch_from_rack)
        return seq.done()

        # if isinstance(instrument, InstrumentSimpler):
        #     self._find_out_sample_pitch_from_simpler(instrument)

    def _find_out_sample_pitch_from_rack(self):
        # type: () -> Sequence
        selected_track = SongFacade.selected_track()
        instrument = cast(InstrumentSimpler, SongFacade.selected_track().instrument)
        seq = Sequence()
        seq.add(partial(self._device_component.select_device, selected_track, instrument.device))
        seq.add(ApplicationViewFacade.toggle_browse)
        seq.wait_ms(1000)
        seq.add(partial(self._browser_service.load_drum_pad_sample, "03-hit Kick Filter.wav"))

        return seq.done()
