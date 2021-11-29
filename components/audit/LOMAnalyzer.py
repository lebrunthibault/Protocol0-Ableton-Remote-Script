from functools import partial

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.sequence.Sequence import Sequence


class LOMAnalyzer(AbstractControlSurfaceComponent):
    """ Audit object model """
    def check_tracks_tree_consistency(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            # 1st layer checks
            if simple_track.group_track:
                assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track

            if simple_track.is_foldable:
                for sub_track in simple_track.sub_tracks:
                    assert sub_track.group_track == simple_track, "failed on %s" % simple_track

            # 2nd layer checks
            abstract_group_track = simple_track.abstract_group_track
            if simple_track.is_foldable:
                assert abstract_group_track.base_track == simple_track, "failed on %s" % simple_track
                assert len(abstract_group_track.sub_tracks) == len(simple_track.sub_tracks)
                for sub_track in abstract_group_track.sub_tracks:
                    if isinstance(sub_track, AbstractGroupTrack):
                        assert sub_track.group_track == abstract_group_track, "failed on %s" % simple_track