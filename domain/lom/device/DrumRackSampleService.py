from typing import cast

from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.Sample.Sample import Sample
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song

def _get_drum_rack(track):
    # type: (SimpleTrack) -> DrumRackDevice
    if not isinstance(track.instrument, InstrumentDrumRack):
        raise Protocol0Warning("track has no drum rack")

    return cast(DrumRackDevice, track.instrument.device)

def _get_selected_sample(track):
    # type: (SimpleTrack) -> Sample
    drum_rack = _get_drum_rack(track)

    return drum_rack.selected_drum_pad.sample

class DrumRackSampleService(object):
    def warp_selected_sample(self):
        # type: () -> None
        sample = _get_selected_sample(Song.selected_track())
        sample.warping = not sample.warping

    def warp_all(self):
        # type: () -> None
        drum_rack = _get_drum_rack(Song.selected_track())

        pads = drum_rack.filled_drum_pads
        assert len(pads) > 0, "no filled pads"

        should_warp = not drum_rack.selected_drum_pad.sample.warping
        # copy warp mode
        warp_mode = drum_rack.selected_drum_pad.sample.warp_mode

        for pad in pads:
            pad.sample.warping = should_warp
            if should_warp:
                pad.sample.warp_mode = warp_mode
