import collections

from typing import Dict, Any

from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.shared.Song import Song

SAMPLE_LOAD_TIME = 24  # ms


class DrumRackStats(object):
    def __init__(self, track_name, drum_rack):
        # type: (str, DrumRackDevice) -> None
        self.track_name = track_name
        self.sample_count = len(drum_rack.filled_drum_pads)

    def __repr__(self):
        # type: () -> str
        return "%s: %s (%sms)" % (
            self.track_name,
            self.sample_count,
            SAMPLE_LOAD_TIME * self.sample_count,
        )


class SampleStats(object):
    def __init__(self):
        # type: () -> None
        instruments = filter(None, [track.instrument for track in Song.simple_tracks()])
        self.drum_racks = [i.device for i in instruments if isinstance(i.device, DrumRackDevice)]
        self.drum_rack_stats = [
            DrumRackStats(track.name, track.instrument.device)
            for track in Song.simple_tracks()
            if track.instrument and isinstance(track.instrument.device, DrumRackDevice)
        ]
        self.drum_rack_stats.sort(key=lambda x: x.sample_count, reverse=True)

        self.simplers = [i.device for i in instruments if isinstance(i.device, SimplerDevice)]

        devices_count = len(self.drum_racks) + len(self.simplers)
        self.count = len(self.simplers) + sum(stat.sample_count for stat in self.drum_rack_stats)
        self.potential_load_time_optimization = (self.count - devices_count) * SAMPLE_LOAD_TIME

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()  # type: Dict[str, Any]
        output["count"] = self.count
        output["total load time"] = "%.2fs" % (float(SAMPLE_LOAD_TIME * self.count) / 1000)
        # output["drum rack count"] = len(self.drum_racks)
        # output["simpler count"] = len(self.simplers)
        output["drum rack stats"] = [str(stat) for stat in self.drum_rack_stats]
        output["possible optimization"] = "%.2fs" % (
            float(self.potential_load_time_optimization) / 1000
        )

        return output
