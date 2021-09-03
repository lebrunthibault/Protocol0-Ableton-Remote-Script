from functools import partial

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.SynchronizableDeviceEnum import SynchronizableDeviceEnum
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import defer


class SetFixerManager(AbstractControlSurfaceComponent):
    """ Do audit and fix operations on a set """

    def check_set(self):
        # type: () -> None
        """ Checks the set is operational """
        self._check_input_routings()
        self._check_tracks_tree_consistency()
        self._check_instruments()

        self.parent.show_message("Set checked !")

    def _check_input_routings(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_audio and not simple_track.is_armable:
                self.parent.log_error("Check the input routing of %s" % simple_track)

    def _check_tracks_tree_consistency(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_foldable:
                assert simple_track.abstract_group_track.base_track == simple_track, "failed on %s" % simple_track
                assert simple_track.abstract_group_track.abstract_group_track is None, "failed on %s" % simple_track
                for sub_track in simple_track.sub_tracks:
                    if sub_track.is_foldable:
                        assert sub_track.abstract_group_track in simple_track.abstract_track.sub_tracks, (
                                "failed on %s" % simple_track
                        )
                    else:
                        assert sub_track in simple_track.abstract_group_track.sub_tracks, "failed on %s" % simple_track
                assert len(simple_track.sub_tracks) == len(simple_track.abstract_group_track.sub_tracks)
            elif simple_track.abstract_group_track:
                assert simple_track in simple_track.abstract_group_track.sub_tracks

            if simple_track.group_track:
                assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track
                if simple_track.is_foldable:
                    assert simple_track.group_track.abstract_group_track, "failed on %s" % simple_track
                    assert (
                            simple_track.abstract_group_track in simple_track.group_track.abstract_group_track.sub_tracks
                        # type: ignore
                    ), ("failed on %s" % simple_track)
                else:
                    assert simple_track.group_track.abstract_group_track is None, "failed on %s" % simple_track
                    assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track

    def _check_instruments(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.instrument and not simple_track.instrument.selected_preset:
                self.parent.log_error(
                    "Couldn't find selected preset of %s (instrument %s)"
                    % (simple_track.abstract_track, simple_track.instrument)
                )

    def refresh_set_appearance(self, log=True):
        # type: (bool) -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""

        self._refresh_tracks_appearance()
        self._refresh_clips_appearance()
        self.refresh_scenes_appearance()
        self._fix_simpler_tracks_name()
        if log:
            self.parent.show_message("Set fixed !")

    def _refresh_clips_appearance(self):
        # type: () -> None
        for clip in (clip for track in self.song.simple_tracks for clip in track.clips):
            clip.refresh_appearance()

    def _refresh_tracks_appearance(self):
        # type: () -> None
        for track in reversed(list(self.song.abstract_tracks)):
            track.refresh_appearance()

    @defer
    def refresh_scenes_appearance(self):
        # type: () -> None
        for scene in self.song.scenes:
            scene.scene_name.update()

    def _fix_simpler_tracks_name(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            if isinstance(track.instrument, InstrumentSimpler):
                if track.base_name.endswith("s"):
                    track.track_name.update(base_name=track.base_name[:-1])

    def update_audio_effect_racks(self):
        # type: () -> Sequence
        seq = Sequence()
        for track in self.song.simple_tracks:
            for device in track.all_devices:
                if isinstance(device, RackDevice) and any(
                        device.name == enum.value for enum in SynchronizableDeviceEnum):
                    seq.add(partial(self.parent.deviceManager.update_audio_effect_rack, device=device))

        return seq.done()
